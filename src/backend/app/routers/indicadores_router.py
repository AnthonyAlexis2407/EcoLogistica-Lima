"""
Router de Indicadores — RF-005 (dashboard operativo y ambiental) y RF-010 (cálculo de compensación de carbono).

Todos los valores salen de la base de datos: ningún indicador es una cifra fija. El dashboard se puede filtrar por distrito
y por rango de fechas (los pedidos por su fecha de creación; las rutas por su fecha de creación).
RBAC: ADMIN_FLOTA, OPERADOR y AUDITOR (lectura).
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_roles
from app.database import get_db
from app.distritos import lista_distritos
from app.models import EmisionCO2, Optimizacion, ParadaRuta, Pedido, Ruta, Usuario, Vehiculo
from app.optimizador import arboles_equivalentes
from app.schemas import IndicadoresOut
from app.servicios import litros_ahorrados

router = APIRouter(prefix="/api/indicadores", tags=["Indicadores (RF-005, RF-010)"])


async def _conteo_por_estado(db: AsyncSession, columna, tabla, *filtros) -> dict[str, int]:
    filas = await db.execute(select(columna, func.count()).select_from(tabla).where(*filtros).group_by(columna))
    conteo = {estado: total for estado, total in filas.all()}
    conteo["TOTAL"] = sum(conteo.values())
    return conteo


def _ahorro(base: float, real: float) -> float:
    return round((base - real) / base * 100.0, 1) if base > 0 else 0.0


@router.get("/distritos", response_model=list[str])
async def distritos(user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR"))):
    """Distritos disponibles para el filtro del dashboard (primero los del este de Lima)."""
    return lista_distritos()


@router.get("/resumen", response_model=IndicadoresOut)
async def resumen_indicadores(
    distrito: str | None = Query(None, max_length=40),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Estado de la flota y los pedidos, rutas activas, combustible ahorrado y CO₂ evitado y compensado."""
    filtros_pedido = []
    if distrito:
        filtros_pedido.append(Pedido.distrito == distrito)
    if desde:
        filtros_pedido.append(Pedido.creado_en >= desde)
    if hasta:
        filtros_pedido.append(Pedido.creado_en <= hasta)
    filtrado = bool(filtros_pedido)

    vehiculos = await _conteo_por_estado(db, Vehiculo.estado, Vehiculo)
    pedidos = await _conteo_por_estado(db, Pedido.estado, Pedido, *filtros_pedido)

    # Las rutas se filtran por las paradas de los pedidos que cumplen el filtro.
    filtros_ruta = []
    if filtrado:
        en_filtro = select(ParadaRuta.ruta_id).join(Pedido, Pedido.pedido_id == ParadaRuta.pedido_id).where(*filtros_pedido)
        filtros_ruta.append(Ruta.ruta_id.in_(en_filtro))

    activas = (await db.execute(
        select(func.count(), func.coalesce(func.sum(Ruta.distancia_km), 0), func.coalesce(func.sum(Ruta.co2_kg), 0))
        .where(Ruta.estado.in_(("PLANIFICADA", "EN_CURSO")), *filtros_ruta)
    )).one()

    ventanas = (await db.execute(
        select(func.count(), func.coalesce(func.sum(case((ParadaRuta.en_ventana.is_(True), 1), else_=0)), 0))
        .select_from(ParadaRuta).join(Ruta, Ruta.ruta_id == ParadaRuta.ruta_id)
        .join(Pedido, Pedido.pedido_id == ParadaRuta.pedido_id)
        .where(Ruta.estado.in_(("PLANIFICADA", "EN_CURSO")), ParadaRuta.en_ventana.is_not(None), *filtros_pedido)
    )).one()
    en_ventana_pct = round(float(ventanas[1]) / ventanas[0] * 100.0, 1) if ventanas[0] else None

    # Acumulado: sin filtro sale de las corridas del optimizador; con filtro, de las rutas que lo cumplen.
    if filtrado:
        rutas = (await db.execute(
            select(Ruta).where(Ruta.estado != "CANCELADA", *filtros_ruta).options(selectinload(Ruta.vehiculo))
        )).scalars().all()
        km_base = sum(float(r.distancia_base_km) for r in rutas)
        km_real = sum(float(r.distancia_km) for r in rutas)
        co2_base = sum(float(r.co2_base_kg) for r in rutas)
        co2_real = sum(float(r.co2_kg) for r in rutas)
        optimizaciones = len({r.optimizacion_id for r in rutas})
    else:
        acumulado = (await db.execute(
            select(
                func.count(),
                func.coalesce(func.sum(Optimizacion.distancia_base_km), 0),
                func.coalesce(func.sum(Optimizacion.distancia_km), 0),
                func.coalesce(func.sum(Optimizacion.co2_base_kg), 0),
                func.coalesce(func.sum(Optimizacion.co2_kg), 0),
            )
        )).one()
        optimizaciones = acumulado[0]
        km_base, km_real, co2_base, co2_real = (float(v) for v in acumulado[1:])
        rutas = (await db.execute(
            select(Ruta).where(Ruta.estado != "CANCELADA").options(selectinload(Ruta.vehiculo))
        )).scalars().all()
    co2_evitado = max(0.0, co2_base - co2_real)
    litros = sum(
        litros_ahorrados(float(r.distancia_base_km), float(r.distancia_km), r.vehiculo.tipo_combustible) for r in rutas
    )

    # Compensación (RN-009): solo rutas COMPLETADAS con su emisión ya registrada.
    comp = (await db.execute(
        select(func.count(), func.coalesce(func.sum(EmisionCO2.kg_co2_evitado), 0),
               func.coalesce(func.sum(EmisionCO2.arboles_equivalentes), 0))
        .select_from(EmisionCO2).join(Ruta, Ruta.ruta_id == EmisionCO2.ruta_id).where(*filtros_ruta)
    )).one()

    return IndicadoresOut(
        vehiculos=vehiculos,
        pedidos=pedidos,
        rutas_activas=activas[0],
        distancia_planificada_km=round(float(activas[1]), 1),
        co2_planificado_kg=round(float(activas[2]), 1),
        pedidos_en_ventana_pct=en_ventana_pct,
        optimizaciones=optimizaciones,
        co2_evitado_kg=round(co2_evitado, 1),
        ahorro_co2_pct=_ahorro(co2_base, co2_real),
        ahorro_km_pct=_ahorro(km_base, km_real),
        arboles_equivalentes=arboles_equivalentes(co2_evitado),
        combustible_ahorrado_litros=round(litros, 1),
        rutas_completadas=comp[0],
        co2_compensado_kg=round(float(comp[1]), 1),
        arboles_compensados=round(float(comp[2]), 2),
        distrito=distrito,
    )
