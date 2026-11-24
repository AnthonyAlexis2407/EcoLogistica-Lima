"""
Router de Reportes — RF-006 (reportes exportables).

Exporta CSV listos para abrir en una hoja de cálculo (UTF-8 con BOM). Las celdas de texto que empiezan con
`=`, `+`, `-`, `@`, tabulador o retorno se prefijan con una comilla simple para impedir la inyección de fórmulas
(OWASP: CSV injection). Los números no se alteran.

RBAC: ADMIN_FLOTA, OPERADOR y AUDITOR.
"""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_roles
from app.database import get_db
from app.models import Optimizacion, ParadaRuta, Pedido, Ruta, Usuario
from app.optimizador import arboles_equivalentes

router = APIRouter(prefix="/api/reportes", tags=["Reportes (RF-006)"])

LIMITE_FILAS = 5000
_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")


def texto_seguro(valor) -> str:
    """Neutraliza fórmulas en una celda de texto."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto.startswith(_PELIGROSOS) else texto


def _fecha(valor: datetime | None) -> str:
    return valor.isoformat(timespec="minutes") if valor else ""


def _csv(nombre: str, encabezados: list[str], filas: list[list]) -> Response:
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\r\n")
    escritor.writerow(encabezados)
    escritor.writerows(filas)
    return Response(
        content="﻿" + salida.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/pedidos.csv")
async def reporte_pedidos(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Todos los pedidos con su estado (máximo 5.000 filas, los más recientes primero)."""
    pedidos = (await db.execute(
        select(Pedido).order_by(Pedido.creado_en.desc(), Pedido.pedido_id).limit(LIMITE_FILAS)
    )).scalars().all()
    filas = [
        [
            p.pedido_id, texto_seguro(p.direccion), float(p.latitud), float(p.longitud), float(p.peso_kg),
            _fecha(p.ventana_inicio), _fecha(p.ventana_fin), p.estado, _fecha(p.creado_en),
        ]
        for p in pedidos
    ]
    return _csv(
        "pedidos.csv",
        ["pedido_id", "direccion", "latitud", "longitud", "peso_kg", "ventana_inicio", "ventana_fin", "estado", "creado_en"],
        filas,
    )


@router.get("/rutas.csv")
async def reporte_rutas(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Una fila por parada de cada ruta, con la distancia y el CO₂ de la ruta."""
    rutas = (await db.execute(
        select(Ruta)
        .options(selectinload(Ruta.paradas).selectinload(ParadaRuta.pedido), selectinload(Ruta.vehiculo))
        .order_by(Ruta.creado_en.desc(), Ruta.ruta_id).limit(LIMITE_FILAS)
    )).scalars().all()
    filas = [
        [
            r.ruta_id, texto_seguro(r.vehiculo.placa), r.vehiculo.tipo_combustible, r.estado, p.orden, p.pedido_id,
            texto_seguro(p.pedido.direccion), float(p.pedido.latitud), float(p.pedido.longitud), float(p.pedido.peso_kg),
            _fecha(p.llegada_estimada), "" if p.en_ventana is None else ("SI" if p.en_ventana else "NO"),
            float(r.distancia_km), float(r.co2_kg),
        ]
        for r in rutas for p in r.paradas
    ]
    return _csv(
        "rutas.csv",
        [
            "ruta_id", "placa", "combustible", "estado_ruta", "orden", "pedido_id", "direccion", "latitud", "longitud",
            "peso_kg", "llegada_estimada", "en_ventana", "distancia_ruta_km", "co2_ruta_kg",
        ],
        filas,
    )


@router.get("/ambiental.csv")
async def reporte_ambiental(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Una fila por optimización: kilómetros, CO₂, CO₂ evitado y su equivalente en árboles (RF-010)."""
    optimizaciones = (await db.execute(
        select(Optimizacion).order_by(Optimizacion.creado_en.desc()).limit(LIMITE_FILAS)
    )).scalars().all()
    filas = []
    for o in optimizaciones:
        base, real = float(o.co2_base_kg), float(o.co2_kg)
        evitado = max(0.0, base - real)
        filas.append([
            o.optimizacion_id, _fecha(o.creado_en), texto_seguro(o.algoritmo), o.pedidos_planificados, o.pedidos_sin_asignar,
            float(o.distancia_km), float(o.distancia_base_km), real, base, round(evitado, 3),
            round(evitado / base * 100.0, 1) if base > 0 else 0.0, arboles_equivalentes(evitado), float(o.tiempo_ms),
        ])
    return _csv(
        "ambiental.csv",
        [
            "optimizacion_id", "fecha", "algoritmo", "pedidos_planificados", "pedidos_sin_asignar", "distancia_km",
            "distancia_base_km", "co2_kg", "co2_base_kg", "co2_evitado_kg", "ahorro_co2_pct", "arboles_equivalentes",
            "tiempo_calculo_ms",
        ],
        filas,
    )
