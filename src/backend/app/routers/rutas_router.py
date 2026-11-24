"""
Router de Rutas — RF-003 (generación y gestión de rutas optimizadas) y RF-004 (datos para el mapa).

RBAC (Documento 08):
- ADMIN_FLOTA y OPERADOR: optimizar, listar y cancelar rutas.
- AUDITOR: solo lectura.
- BODEGA y CONDUCTOR: sin acceso (la BODEGA ve el estado de sus pedidos en el módulo de pedidos).
"""

import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_roles
from app.config import settings
from app.database import get_db
from app.models import Optimizacion, ParadaRuta, Pedido, RestriccionVehicular, Ruta, Usuario, Vehiculo
from app.optimizador import Camion, Punto, arboles_equivalentes, optimizar
from app.schemas import (
    DepositoOut,
    MensajeResponse,
    OptimizacionOut,
    OptimizarRequest,
    ParadaOut,
    RutaOut,
    RutasActivasOut,
    SinAsignarOut,
    VehiculoExcluidoOut,
)

router = APIRouter(prefix="/api/rutas", tags=["Rutas (RF-003)"])

# RNF-006: el diseño apunta a 1.000 pedidos por día; el tope protege la API de una carga mayor.
MAX_PEDIDOS_POR_OPTIMIZACION = 1000
LIMA = timezone(timedelta(hours=-5))  # Perú no usa horario de verano

_CON_DETALLE = (
    selectinload(Ruta.paradas).selectinload(ParadaRuta.pedido),
    selectinload(Ruta.vehiculo),
)


def _ruta_out(ruta: Ruta) -> RutaOut:
    return RutaOut(
        ruta_id=ruta.ruta_id,
        vehiculo_id=ruta.vehiculo_id,
        placa=ruta.vehiculo.placa,
        tipo_combustible=ruta.vehiculo.tipo_combustible,
        capacidad_kg=float(ruta.vehiculo.capacidad_kg),
        estado=ruta.estado,
        distancia_km=float(ruta.distancia_km),
        carga_kg=float(ruta.carga_kg),
        co2_kg=float(ruta.co2_kg),
        duracion_min=float(ruta.duracion_min),
        paradas=[
            ParadaOut(
                pedido_id=p.pedido_id,
                orden=p.orden,
                direccion=p.pedido.direccion,
                latitud=float(p.pedido.latitud),
                longitud=float(p.pedido.longitud),
                peso_kg=float(p.pedido.peso_kg),
                distancia_desde_anterior_km=float(p.distancia_desde_anterior_km),
                llegada_estimada=p.llegada_estimada,
                espera_min=float(p.espera_min),
                en_ventana=p.en_ventana,
            )
            for p in ruta.paradas
        ],
    )


async def _cargar_rutas(db: AsyncSession, *filtros) -> list[Ruta]:
    resultado = await db.execute(
        select(Ruta).where(*filtros).options(*_CON_DETALLE).order_by(Ruta.creado_en.desc(), Ruta.ruta_id)
    )
    return list(resultado.scalars().all())


@router.post("/optimizar", response_model=OptimizacionOut, status_code=status.HTTP_201_CREATED)
async def optimizar_rutas(
    payload: OptimizarRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """
    Planifica las rutas de todos los pedidos PENDIENTE con los vehículos DISPONIBLES que no tienen una ruta planificada.

    Los pedidos asignados pasan a ASIGNADO. Los que no caben en ningún vehículo se informan con su motivo.
    El cálculo corre fuera del bucle de eventos y respeta el límite de tiempo (SLA de 45 s, RNF-001).
    """
    limite = payload.limite_segundos if payload else settings.OPTIMIZADOR_LIMITE_SEGUNDOS

    pedidos = (await db.execute(
        select(Pedido).where(Pedido.estado == "PENDIENTE").order_by(Pedido.creado_en, Pedido.pedido_id)
        .limit(MAX_PEDIDOS_POR_OPTIMIZACION)
    )).scalars().all()
    if not pedidos:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No hay pedidos pendientes para planificar")

    ocupados = select(Ruta.vehiculo_id).where(Ruta.estado == "PLANIFICADA")
    vehiculos = (await db.execute(
        select(Vehiculo).where(Vehiculo.estado == "DISPONIBLE", Vehiculo.vehiculo_id.not_in(ocupados))
    )).scalars().all()

    # RN-002 (Pico y Placa): un vehículo restringido hoy y sin exoneración no entra al cálculo.
    dia_hoy = datetime.now(LIMA).isoweekday()  # 1 = lunes … 7 = domingo, como en el DDL
    restringidos = set((await db.execute(
        select(RestriccionVehicular.vehiculo_id).where(
            RestriccionVehicular.dia_restringido == dia_hoy, RestriccionVehicular.exonerado.is_(False),
        )
    )).scalars().all())
    excluidos: list[VehiculoExcluidoOut] = []
    aptos = []
    for v in vehiculos:
        if v.vehiculo_id in restringidos:
            motivo = "Restringido por Pico y Placa hoy, sin exoneración (RN-002)"
            excluidos.append(VehiculoExcluidoOut(placa=v.placa, motivo=motivo))
        elif v.factor_emision_co2 is None:
            # RF-010: sin factor de emisión no se puede calcular el CO₂; se pide completar el dato de la ficha técnica.
            motivo = "Falta el factor de emisión de CO₂ en su ficha técnica"
            excluidos.append(VehiculoExcluidoOut(placa=v.placa, motivo=motivo))
        else:
            aptos.append(v)
    vehiculos = aptos

    puntos = [
        Punto(
            id=p.pedido_id, latitud=float(p.latitud), longitud=float(p.longitud), peso_kg=float(p.peso_kg),
            ventana_inicio=p.ventana_inicio, ventana_fin=p.ventana_fin,
        )
        for p in pedidos
    ]
    camiones = [
        Camion(
            id=v.vehiculo_id, placa=v.placa, capacidad_kg=float(v.capacidad_kg), combustible=v.tipo_combustible,
            factor_co2=float(v.factor_emision_co2) if v.factor_emision_co2 is not None else None,
        )
        for v in vehiculos
    ]

    plan = await asyncio.to_thread(
        optimizar, puntos, camiones, (settings.DEPOSITO_LATITUD, settings.DEPOSITO_LONGITUD), limite,
    )

    por_id = {p.pedido_id: p for p in pedidos}
    opt = Optimizacion(
        creado_por=user.usuario_id, algoritmo=plan.algoritmo,
        pedidos_planificados=sum(len(r.paradas) for r in plan.rutas),
        pedidos_sin_asignar=len(plan.sin_asignar),
        distancia_km=plan.distancia_total_km, distancia_base_km=plan.distancia_base_km,
        co2_kg=plan.co2_total_kg, co2_base_kg=plan.co2_base_kg,
        tiempo_ms=plan.tiempo_ms, limite_alcanzado=plan.limite_alcanzado,
    )
    db.add(opt)
    await db.flush()

    for r in plan.rutas:
        ruta = Ruta(
            optimizacion_id=opt.optimizacion_id, vehiculo_id=r.camion_id, estado="PLANIFICADA",
            distancia_km=r.distancia_km, carga_kg=r.carga_kg, co2_kg=r.co2_kg, duracion_min=r.duracion_min,
        )
        db.add(ruta)
        await db.flush()
        for parada in r.paradas:
            db.add(ParadaRuta(
                ruta_id=ruta.ruta_id, pedido_id=parada.punto_id, orden=parada.orden,
                distancia_desde_anterior_km=parada.distancia_desde_anterior_km,
                llegada_estimada=parada.llegada, espera_min=parada.espera_min, en_ventana=parada.en_ventana,
            ))
            por_id[parada.punto_id].estado = "ASIGNADO"
    await db.flush()

    rutas = await _cargar_rutas(db, Ruta.optimizacion_id == opt.optimizacion_id)
    return OptimizacionOut(
        optimizacion_id=opt.optimizacion_id, algoritmo=plan.algoritmo,
        pedidos_planificados=opt.pedidos_planificados, pedidos_sin_asignar=opt.pedidos_sin_asignar,
        distancia_km=plan.distancia_total_km, distancia_base_km=plan.distancia_base_km, ahorro_km_pct=plan.ahorro_km_pct,
        co2_kg=plan.co2_total_kg, co2_base_kg=plan.co2_base_kg, co2_evitado_kg=round(plan.co2_evitado_kg, 3),
        ahorro_co2_pct=plan.ahorro_co2_pct, arboles_equivalentes=arboles_equivalentes(plan.co2_evitado_kg),
        tiempo_ms=plan.tiempo_ms, limite_alcanzado=plan.limite_alcanzado,
        rutas=[_ruta_out(r) for r in sorted(rutas, key=lambda x: -float(x.carga_kg))],
        sin_asignar=[SinAsignarOut(pedido_id=pid, motivo=motivo) for pid, motivo in plan.sin_asignar],
        vehiculos_excluidos=excluidos,
    )


@router.get("/", response_model=RutasActivasOut)
async def listar_rutas_activas(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Rutas planificadas con sus paradas y coordenadas, más el depósito: es lo que dibuja el mapa (RF-004)."""
    rutas = await _cargar_rutas(db, Ruta.estado == "PLANIFICADA")
    return RutasActivasOut(
        deposito=DepositoOut(latitud=settings.DEPOSITO_LATITUD, longitud=settings.DEPOSITO_LONGITUD),
        rutas=[_ruta_out(r) for r in rutas],
    )


@router.post("/{ruta_id}/cancelar", response_model=MensajeResponse)
async def cancelar_ruta(
    ruta_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """Cancela una ruta planificada: libera el vehículo y devuelve sus pedidos a PENDIENTE para volver a planificarlos."""
    rutas = await _cargar_rutas(db, Ruta.ruta_id == ruta_id)
    if not rutas:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    ruta = rutas[0]
    if ruta.estado == "CANCELADA":
        raise HTTPException(status_code=400, detail="La ruta ya se encuentra cancelada")

    ruta.estado = "CANCELADA"
    liberados = 0
    for parada in ruta.paradas:
        if parada.pedido.estado == "ASIGNADO":
            parada.pedido.estado = "PENDIENTE"
            liberados += 1
    await db.flush()
    return MensajeResponse(mensaje=f"Ruta {ruta_id} cancelada; {liberados} pedido(s) vuelven a PENDIENTE")
