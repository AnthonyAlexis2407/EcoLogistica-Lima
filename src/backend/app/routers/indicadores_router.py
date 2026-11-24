"""
Router de Indicadores — RF-005 (dashboard operativo y ambiental) y RF-010 (cálculo de compensación de carbono).

Todos los valores salen de la base de datos: ningún indicador es una cifra fija.
RBAC: ADMIN_FLOTA, OPERADOR y AUDITOR (lectura).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.database import get_db
from app.models import Optimizacion, ParadaRuta, Pedido, Ruta, Usuario, Vehiculo
from app.optimizador import arboles_equivalentes
from app.schemas import IndicadoresOut

router = APIRouter(prefix="/api/indicadores", tags=["Indicadores (RF-005, RF-010)"])


async def _conteo_por_estado(db: AsyncSession, columna, tabla) -> dict[str, int]:
    filas = await db.execute(select(columna, func.count()).select_from(tabla).group_by(columna))
    conteo = {estado: total for estado, total in filas.all()}
    conteo["TOTAL"] = sum(conteo.values())
    return conteo


def _ahorro(base: float, real: float) -> float:
    return round((base - real) / base * 100.0, 1) if base > 0 else 0.0


@router.get("/resumen", response_model=IndicadoresOut)
async def resumen_indicadores(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Estado de la flota y los pedidos, rutas activas y CO₂ evitado de forma acumulada."""
    vehiculos = await _conteo_por_estado(db, Vehiculo.estado, Vehiculo)
    pedidos = await _conteo_por_estado(db, Pedido.estado, Pedido)

    activas = (await db.execute(
        select(func.count(), func.coalesce(func.sum(Ruta.distancia_km), 0), func.coalesce(func.sum(Ruta.co2_kg), 0))
        .where(Ruta.estado == "PLANIFICADA")
    )).one()

    ventanas = (await db.execute(
        select(func.count(), func.coalesce(func.sum(case((ParadaRuta.en_ventana.is_(True), 1), else_=0)), 0))
        .select_from(ParadaRuta).join(Ruta, Ruta.ruta_id == ParadaRuta.ruta_id)
        .where(Ruta.estado == "PLANIFICADA", ParadaRuta.en_ventana.is_not(None))
    )).one()
    en_ventana_pct = round(float(ventanas[1]) / ventanas[0] * 100.0, 1) if ventanas[0] else None

    acumulado = (await db.execute(
        select(
            func.count(),
            func.coalesce(func.sum(Optimizacion.distancia_base_km), 0),
            func.coalesce(func.sum(Optimizacion.distancia_km), 0),
            func.coalesce(func.sum(Optimizacion.co2_base_kg), 0),
            func.coalesce(func.sum(Optimizacion.co2_kg), 0),
        )
    )).one()
    km_base, km_real, co2_base, co2_real = (float(v) for v in acumulado[1:])
    co2_evitado = max(0.0, co2_base - co2_real)

    return IndicadoresOut(
        vehiculos=vehiculos,
        pedidos=pedidos,
        rutas_activas=activas[0],
        distancia_planificada_km=round(float(activas[1]), 1),
        co2_planificado_kg=round(float(activas[2]), 1),
        pedidos_en_ventana_pct=en_ventana_pct,
        optimizaciones=acumulado[0],
        co2_evitado_kg=round(co2_evitado, 1),
        ahorro_co2_pct=_ahorro(co2_base, co2_real),
        ahorro_km_pct=_ahorro(km_base, km_real),
        arboles_equivalentes=arboles_equivalentes(co2_evitado),
    )
