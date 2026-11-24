"""
Router de Rutas — RF-003 (generación y gestión), RF-004 (mapa), RF-007 (incidencias y re-optimización) y RF-008
(asignación de conductor y ciclo de vida de la ruta).

Ciclo de vida: PLANIFICADA → EN_CURSO → COMPLETADA; también CANCELADA e INTERRUMPIDA (avería).

RBAC (Documento 08):
- ADMIN_FLOTA y OPERADOR: optimizar, asignar conductor, iniciar, completar, cancelar y registrar incidencias.
- CONDUCTOR: iniciar y completar solo su propia ruta.
- AUDITOR: solo lectura.
- BODEGA: sin acceso (ve el estado de sus pedidos y sus notificaciones).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.config import settings
from app.database import get_db
from app.models import Conductor, Incidencia, Pedido, Ruta, Usuario
from app.optimizador import arboles_equivalentes
from app.schemas import (
    AsignarConductor,
    DepositoOut,
    IncidenciaCreate,
    IncidenciaOut,
    MensajeResponse,
    OptimizacionOut,
    OptimizarRequest,
    ReoptimizacionOut,
    RutaOut,
    RutasActivasOut,
    SinAsignarOut,
)
from app.servicios import (
    MAX_PEDIDOS_POR_OPTIMIZACION,
    Notificador,
    ahora,
    cargar_rutas,
    completar_ruta,
    parada_resuelta,
    planificar,
    reoptimizar_ruta,
    ruta_out,
)

router = APIRouter(prefix="/api/rutas", tags=["Rutas (RF-003, RF-007, RF-008)"])

ESTADOS_ABIERTOS = ("PLANIFICADA", "EN_CURSO")


async def _ruta_o_404(db: AsyncSession, ruta_id: str) -> Ruta:
    rutas = await cargar_rutas(db, Ruta.ruta_id == ruta_id)
    if not rutas:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return rutas[0]


async def _verificar_propiedad(db: AsyncSession, ruta: Ruta, user: Usuario) -> None:
    """Un conductor solo opera su propia ruta; el resto de roles permitidos opera cualquiera."""
    if user.rol != "CONDUCTOR":
        return
    propio = (await db.execute(select(Conductor).where(Conductor.usuario_id == user.usuario_id))).scalar_one_or_none()
    if propio is None or ruta.conductor_id != propio.conductor_id:
        raise HTTPException(status_code=403, detail="Solo puede operar la ruta que tiene asignada")


@router.post("/optimizar", response_model=OptimizacionOut, status_code=status.HTTP_201_CREATED)
async def optimizar_rutas(
    payload: OptimizarRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """
    Planifica las rutas de todos los pedidos PENDIENTE con los vehículos DISPONIBLES que no tienen una ruta abierta.

    Respeta capacidad (peso y volumen), ventanas horarias, Pico y Placa y zonas protegidas. Los pedidos asignados pasan
    a ASIGNADO y la bodega recibe su aviso con la hora estimada. Los que no caben se informan con su motivo.
    """
    pedidos = (await db.execute(
        select(Pedido).where(Pedido.estado == "PENDIENTE").order_by(Pedido.creado_en, Pedido.pedido_id)
        .limit(MAX_PEDIDOS_POR_OPTIMIZACION)
    )).scalars().all()
    if not pedidos:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No hay pedidos pendientes para planificar")

    limite = payload.limite_segundos if payload else None
    res = await planificar(db, list(pedidos), user, limite=limite)
    plan = res.plan
    return OptimizacionOut(
        optimizacion_id=res.opt.optimizacion_id, algoritmo=plan.algoritmo,
        pedidos_planificados=res.opt.pedidos_planificados, pedidos_sin_asignar=res.opt.pedidos_sin_asignar,
        distancia_km=plan.distancia_total_km, distancia_base_km=plan.distancia_base_km, ahorro_km_pct=plan.ahorro_km_pct,
        co2_kg=plan.co2_total_kg, co2_base_kg=plan.co2_base_kg, co2_evitado_kg=round(plan.co2_evitado_kg, 3),
        ahorro_co2_pct=plan.ahorro_co2_pct, arboles_equivalentes=arboles_equivalentes(plan.co2_evitado_kg),
        tiempo_ms=plan.tiempo_ms, limite_alcanzado=plan.limite_alcanzado, desde_cache=plan.desde_cache,
        rutas=[ruta_out(r) for r in sorted(res.rutas, key=lambda x: -float(x.carga_kg))],
        sin_asignar=[SinAsignarOut(pedido_id=pid, motivo=motivo) for pid, motivo in plan.sin_asignar],
        vehiculos_excluidos=res.excluidos,
    )


@router.get("/", response_model=RutasActivasOut)
async def listar_rutas_activas(
    estado: str | None = Query(None, pattern=r"^(PLANIFICADA|EN_CURSO|COMPLETADA|CANCELADA|INTERRUMPIDA)$"),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Rutas abiertas (planificadas o en curso) con sus paradas y el depósito: es lo que dibuja el mapa (RF-004)."""
    filtro = Ruta.estado == estado if estado else Ruta.estado.in_(ESTADOS_ABIERTOS)
    rutas = await cargar_rutas(db, filtro)
    return RutasActivasOut(
        deposito=DepositoOut(latitud=settings.DEPOSITO_LATITUD, longitud=settings.DEPOSITO_LONGITUD),
        rutas=[ruta_out(r) for r in rutas],
    )


@router.get("/{ruta_id}", response_model=RutaOut)
async def obtener_ruta(
    ruta_id: str, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR", "CONDUCTOR")),
):
    ruta = await _ruta_o_404(db, ruta_id)
    await _verificar_propiedad(db, ruta, user)
    return ruta_out(ruta)


@router.post("/{ruta_id}/conductor", response_model=RutaOut)
async def asignar_conductor(
    ruta_id: str, payload: AsignarConductor, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """Asigna un conductor activo a la ruta; un conductor solo puede tener una ruta abierta a la vez."""
    ruta = await _ruta_o_404(db, ruta_id)
    if ruta.estado != "PLANIFICADA":
        raise HTTPException(status_code=409, detail="Solo se asigna conductor a una ruta planificada")
    conductor = await db.get(Conductor, payload.conductor_id)
    if conductor is None or not conductor.activo:
        raise HTTPException(status_code=404, detail="Conductor no encontrado o inactivo")
    ocupado = (await db.execute(
        select(Ruta.ruta_id).where(
            Ruta.conductor_id == conductor.conductor_id, Ruta.estado.in_(ESTADOS_ABIERTOS), Ruta.ruta_id != ruta_id,
        )
    )).first()
    if ocupado:
        raise HTTPException(status_code=409, detail="El conductor ya tiene otra ruta abierta")
    ruta.conductor_id = conductor.conductor_id
    await db.flush()
    return ruta_out((await cargar_rutas(db, Ruta.ruta_id == ruta_id))[0])


@router.post("/{ruta_id}/iniciar", response_model=RutaOut)
async def iniciar_ruta(
    ruta_id: str, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "CONDUCTOR")),
):
    """Inicia la ruta: los pedidos pasan a EN_RUTA y cada bodega recibe su aviso con la hora estimada (RF-009)."""
    ruta = await _ruta_o_404(db, ruta_id)
    await _verificar_propiedad(db, ruta, user)
    if ruta.estado != "PLANIFICADA":
        raise HTTPException(status_code=409, detail="Solo se inicia una ruta planificada")
    if ruta.conductor_id is None:
        raise HTTPException(status_code=409, detail="Asigne un conductor antes de iniciar la ruta")
    ruta.estado = "EN_CURSO"
    ruta.iniciada_en = ahora()
    notificador = Notificador(db)
    for parada in ruta.paradas:
        if parada.estado == "PENDIENTE":
            parada.pedido.estado = "EN_RUTA"
            await notificador.avisar(
                parada.pedido, "EN_RUTA", "Su pedido salió en ruta de entrega.", parada.llegada_estimada,
            )
    await db.flush()
    return ruta_out(ruta)


@router.post("/{ruta_id}/completar", response_model=MensajeResponse)
async def completar(
    ruta_id: str, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "CONDUCTOR")),
):
    """Cierra la ruta cuando todas sus paradas están resueltas y registra la emisión de CO₂ y su compensación."""
    ruta = await _ruta_o_404(db, ruta_id)
    await _verificar_propiedad(db, ruta, user)
    if ruta.estado != "EN_CURSO":
        raise HTTPException(status_code=409, detail="Solo se completa una ruta en curso")
    pendientes = [p for p in ruta.paradas if not parada_resuelta(p)]
    if pendientes:
        raise HTTPException(status_code=409, detail=f"Quedan {len(pendientes)} parada(s) sin entregar o reprogramar")
    try:
        emision = await completar_ruta(db, ruta)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return MensajeResponse(
        mensaje=f"Ruta completada. CO₂ evitado: {float(emision.kg_co2_evitado):.2f} kg "
                f"({float(emision.arboles_equivalentes):.2f} árboles equivalentes)"
    )


@router.post("/{ruta_id}/cancelar", response_model=MensajeResponse)
async def cancelar_ruta(
    ruta_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """Cancela una ruta abierta: libera el vehículo y devuelve sus pedidos a PENDIENTE para volver a planificarlos."""
    ruta = await _ruta_o_404(db, ruta_id)
    if ruta.estado == "CANCELADA":
        raise HTTPException(status_code=400, detail="La ruta ya se encuentra cancelada")
    if ruta.estado not in ESTADOS_ABIERTOS:
        raise HTTPException(status_code=409, detail="Solo se cancela una ruta planificada o en curso")

    ruta.estado = "CANCELADA"
    liberados = 0
    for parada in ruta.paradas:
        if parada.pedido.estado in ("ASIGNADO", "EN_RUTA") and parada.estado == "PENDIENTE":
            parada.pedido.estado = "PENDIENTE"
            parada.estado = "RETIRADA"
            parada.motivo = "Ruta cancelada"
            liberados += 1
    await db.flush()
    return MensajeResponse(mensaje=f"Ruta {ruta_id} cancelada; {liberados} pedido(s) vuelven a PENDIENTE")


@router.post("/{ruta_id}/incidencias", response_model=ReoptimizacionOut, status_code=status.HTTP_201_CREATED)
async def registrar_incidencia(
    ruta_id: str, payload: IncidenciaCreate, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """
    Registra una incidencia (vía cerrada, accidente, avería o pedido cancelado) y re-optimiza lo que falta de la ruta
    en menos de 45 s (RF-007). Una avería redistribuye los pedidos en otros vehículos.
    """
    ruta = await _ruta_o_404(db, ruta_id)
    if ruta.estado not in ESTADOS_ABIERTOS:
        raise HTTPException(status_code=409, detail="Solo se registran incidencias en una ruta abierta")
    if payload.tipo in ("VIA_CERRADA", "ACCIDENTE") and (payload.latitud is None or payload.longitud is None):
        raise HTTPException(status_code=422, detail="Indique la ubicación (latitud y longitud) del evento")
    if payload.tipo == "PEDIDO_CANCELADO" and not payload.pedido_id:
        raise HTTPException(status_code=422, detail="Indique el pedido cancelado")
    try:
        return await reoptimizar_ruta(
            db, ruta, user, tipo=payload.tipo, descripcion=payload.descripcion, latitud=payload.latitud,
            longitud=payload.longitud, radio_km=payload.radio_km, pedido_id=payload.pedido_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{ruta_id}/incidencias", response_model=list[IncidenciaOut])
async def listar_incidencias(
    ruta_id: str, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    filas = await db.execute(
        select(Incidencia).where(Incidencia.ruta_id == ruta_id).order_by(Incidencia.creado_en.desc())
    )
    return filas.scalars().all()
