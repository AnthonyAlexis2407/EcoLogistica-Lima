"""
Router de Reportes — RF-006 (reportes exportables en CSV, Excel y PDF).

Tres reportes (`pedidos`, `rutas`, `ambiental`) en tres formatos (`csv`, `xlsx`, `pdf`), con filtros opcionales por
distrito y rango de fechas. Los CSV son UTF-8 con BOM; las celdas de texto que empiezan con `=`, `+`, `-`, `@`, tabulador
o retorno se prefijan con una comilla simple para impedir la inyección de fórmulas (OWASP: CSV injection).

Privacidad (RNF-008): el rol AUDITOR recibe los reportes SIN datos personales ni de geolocalización (sin dirección ni
coordenadas); ADMIN_FLOTA y OPERADOR reciben el detalle completo.

RBAC: ADMIN_FLOTA, OPERADOR y AUDITOR.
"""

import csv
import io
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_roles
from app.database import get_db
from app.exportar import generar_pdf, generar_xlsx
from app.models import Optimizacion, ParadaRuta, Pedido, Ruta, Usuario
from app.optimizador import arboles_equivalentes

router = APIRouter(prefix="/api/reportes", tags=["Reportes (RF-006)"])

LIMITE_FILAS = 5000
_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")
_TIPOS = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


def texto_seguro(valor) -> str:
    """Neutraliza fórmulas en una celda de texto."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto.startswith(_PELIGROSOS) else texto


def _fecha(valor: datetime | None) -> str:
    return valor.isoformat(timespec="minutes") if valor else ""


def _respuesta(
    formato: str, nombre: str, titulo: str, encabezados: list[str], filas: list[list], subtitulo: str,
) -> Response:
    if formato == "csv":
        salida = io.StringIO()
        escritor = csv.writer(salida, lineterminator="\r\n")
        escritor.writerow(encabezados)
        escritor.writerows([[texto_seguro(v) if isinstance(v, str) else v for v in fila] for fila in filas])
        contenido: str | bytes = "﻿" + salida.getvalue()
    elif formato == "xlsx":
        contenido = generar_xlsx(encabezados, filas, hoja=titulo)
    else:
        contenido = generar_pdf(titulo, encabezados, filas, subtitulo)
    return Response(
        content=contenido, media_type=_TIPOS[formato],
        headers={"Content-Disposition": f'attachment; filename="{nombre}.{formato}"'},
    )


def _subtitulo(user: Usuario, distrito: str | None, desde: datetime | None, hasta: datetime | None) -> str:
    partes = [f"Generado: {datetime.now():%Y-%m-%d %H:%M}"]
    if distrito:
        partes.append(f"Distrito: {distrito}")
    if desde or hasta:
        partes.append(f"Periodo: {_fecha(desde) or 'inicio'} a {_fecha(hasta) or 'hoy'}")
    if user.rol == "AUDITOR":
        partes.append("Sin datos personales ni de geolocalizacion")
    return " | ".join(partes)


def _filtros_pedido(distrito: str | None, desde: datetime | None, hasta: datetime | None) -> list:
    filtros = []
    if distrito:
        filtros.append(Pedido.distrito == distrito)
    if desde:
        filtros.append(Pedido.creado_en >= desde)
    if hasta:
        filtros.append(Pedido.creado_en <= hasta)
    return filtros


async def _datos_pedidos(db: AsyncSession, anonimo: bool, filtros: list) -> tuple[list[str], list[list]]:
    pedidos = (await db.execute(
        select(Pedido).where(*filtros).order_by(Pedido.creado_en.desc(), Pedido.pedido_id).limit(LIMITE_FILAS)
    )).scalars().all()
    if anonimo:
        encabezados = [
            "pedido_id", "distrito", "peso_kg", "volumen_m3", "ventana_inicio", "ventana_fin", "estado", "creado_en",
        ]
        filas = [
            [p.pedido_id, p.distrito or "", float(p.peso_kg), float(p.volumen_m3 or 0), _fecha(p.ventana_inicio),
             _fecha(p.ventana_fin), p.estado, _fecha(p.creado_en)]
            for p in pedidos
        ]
        return encabezados, filas
    encabezados = [
        "pedido_id", "direccion", "latitud", "longitud", "peso_kg", "ventana_inicio", "ventana_fin", "estado", "creado_en",
        "volumen_m3", "distrito",
    ]
    filas = [
        [
            p.pedido_id, p.direccion, float(p.latitud), float(p.longitud), float(p.peso_kg),
            _fecha(p.ventana_inicio), _fecha(p.ventana_fin), p.estado, _fecha(p.creado_en),
            float(p.volumen_m3 or 0), p.distrito or "",
        ]
        for p in pedidos
    ]
    return encabezados, filas


async def _datos_rutas(
    db: AsyncSession, anonimo: bool, distrito: str | None, desde: datetime | None, hasta: datetime | None,
) -> tuple[list[str], list[list]]:
    filtros = _filtros_pedido(distrito, desde, hasta)
    consulta = select(Ruta).options(
        selectinload(Ruta.paradas).selectinload(ParadaRuta.pedido), selectinload(Ruta.vehiculo),
    ).order_by(Ruta.creado_en.desc(), Ruta.ruta_id).limit(LIMITE_FILAS)
    if filtros:
        consulta = consulta.where(Ruta.ruta_id.in_(
            select(ParadaRuta.ruta_id).join(Pedido, Pedido.pedido_id == ParadaRuta.pedido_id).where(*filtros)
        ))
    rutas = (await db.execute(consulta)).scalars().all()
    if anonimo:
        encabezados = [
            "ruta_id", "placa", "combustible", "estado_ruta", "orden", "pedido_id", "distrito", "peso_kg",
            "llegada_estimada", "en_ventana", "distancia_ruta_km", "co2_ruta_kg",
        ]
        filas = [
            [r.ruta_id, r.vehiculo.placa, r.vehiculo.tipo_combustible, r.estado, p.orden, p.pedido_id,
             p.pedido.distrito or "", float(p.pedido.peso_kg), _fecha(p.llegada_estimada),
             "" if p.en_ventana is None else ("SI" if p.en_ventana else "NO"), float(r.distancia_km), float(r.co2_kg)]
            for r in rutas for p in r.paradas if not filtros or _cumple(p.pedido, distrito, desde, hasta)
        ]
        return encabezados, filas
    encabezados = [
        "ruta_id", "placa", "combustible", "estado_ruta", "orden", "pedido_id", "direccion", "latitud", "longitud",
        "peso_kg", "llegada_estimada", "en_ventana", "distancia_ruta_km", "co2_ruta_kg", "estado_parada", "distrito",
    ]
    filas = [
        [
            r.ruta_id, r.vehiculo.placa, r.vehiculo.tipo_combustible, r.estado, p.orden, p.pedido_id,
            p.pedido.direccion, float(p.pedido.latitud), float(p.pedido.longitud), float(p.pedido.peso_kg),
            _fecha(p.llegada_estimada), "" if p.en_ventana is None else ("SI" if p.en_ventana else "NO"),
            float(r.distancia_km), float(r.co2_kg), p.estado, p.pedido.distrito or "",
        ]
        for r in rutas for p in r.paradas if not filtros or _cumple(p.pedido, distrito, desde, hasta)
    ]
    return encabezados, filas


def _naive_utc(valor: datetime) -> datetime:
    return valor.astimezone(timezone.utc).replace(tzinfo=None) if valor.tzinfo else valor


def _cumple(pedido: Pedido, distrito: str | None, desde: datetime | None, hasta: datetime | None) -> bool:
    """Las paradas se filtran con las mismas condiciones del pedido (distrito y fechas de creación)."""
    if distrito and pedido.distrito != distrito:
        return False
    creado = _naive_utc(pedido.creado_en) if pedido.creado_en else None
    if desde and creado and creado < _naive_utc(desde):
        return False
    return not (hasta and creado and creado > _naive_utc(hasta))


async def _datos_ambiental(db: AsyncSession, desde: datetime | None, hasta: datetime | None) -> tuple[list[str], list[list]]:
    consulta = select(Optimizacion).order_by(Optimizacion.creado_en.desc()).limit(LIMITE_FILAS)
    if desde:
        consulta = consulta.where(Optimizacion.creado_en >= desde)
    if hasta:
        consulta = consulta.where(Optimizacion.creado_en <= hasta)
    optimizaciones = (await db.execute(consulta)).scalars().all()
    filas = []
    for o in optimizaciones:
        base, real = float(o.co2_base_kg), float(o.co2_kg)
        evitado = max(0.0, base - real)
        filas.append([
            o.optimizacion_id, _fecha(o.creado_en), o.algoritmo, o.pedidos_planificados, o.pedidos_sin_asignar,
            float(o.distancia_km), float(o.distancia_base_km), real, base, round(evitado, 3),
            round(evitado / base * 100.0, 1) if base > 0 else 0.0, arboles_equivalentes(evitado), float(o.tiempo_ms),
        ])
    encabezados = [
        "optimizacion_id", "fecha", "algoritmo", "pedidos_planificados", "pedidos_sin_asignar", "distancia_km",
        "distancia_base_km", "co2_kg", "co2_base_kg", "co2_evitado_kg", "ahorro_co2_pct", "arboles_equivalentes",
        "tiempo_calculo_ms",
    ]
    return encabezados, filas


@router.get("/{reporte}.{formato}")
async def exportar_reporte(
    reporte: Literal["pedidos", "rutas", "ambiental"],
    formato: Literal["csv", "xlsx", "pdf"],
    distrito: str | None = Query(None, max_length=40),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Descarga el reporte pedido (máximo 5.000 filas, los más recientes primero)."""
    anonimo = user.rol == "AUDITOR"
    filtros = _filtros_pedido(distrito, desde, hasta)
    if reporte == "pedidos":
        encabezados, filas = await _datos_pedidos(db, anonimo, filtros)
    elif reporte == "rutas":
        encabezados, filas = await _datos_rutas(db, anonimo, distrito, desde, hasta)
    else:
        encabezados, filas = await _datos_ambiental(db, desde, hasta)
    titulo = {"pedidos": "Reporte de pedidos", "rutas": "Reporte de rutas", "ambiental": "Reporte ambiental"}[reporte]
    return _respuesta(formato, reporte, titulo, encabezados, filas, _subtitulo(user, distrito, desde, hasta))
