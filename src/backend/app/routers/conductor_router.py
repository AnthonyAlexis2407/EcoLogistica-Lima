"""
Router del Conductor — RF-004 (ruta en el móvil, desvío de GPS) y RF-008 (entregas con evidencia, reprogramación y
sincronización sin conexión).

RBAC: solo el rol CONDUCTOR, y únicamente sobre las paradas de su propia ruta.

Entregas sin conexión (RNF-010): la aplicación guarda cada acción en una cola con una `clave_sync` única y la envía en lote
a `/sync` cuando vuelve la red. La clave hace la operación idempotente: reenviar una acción ya aplicada no la duplica.
"""

import math
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import require_roles
from app.config import settings
from app.database import get_db
from app.models import Conductor, ParadaRuta, Ruta, Usuario
from app.optimizador import RADIO_TIERRA_KM
from app.schemas import (
    EntregaIn,
    EntregaOut,
    ReprogramarIn,
    ResultadoSync,
    RutaOut,
    SyncIn,
    SyncOut,
    UbicacionIn,
    UbicacionOut,
)
from app.servicios import (
    UMBRAL_DESVIO_KM,
    Notificador,
    ahora,
    cargar_rutas,
    parada_resuelta,
    reoptimizar_ruta,
    ruta_out,
    utc,
)

router = APIRouter(prefix="/api/conductor", tags=["Conductor (RF-004, RF-008)"])
_SOLO_CONDUCTOR = require_roles("CONDUCTOR")


async def _conductor(db: AsyncSession, user: Usuario) -> Conductor:
    conductor = (await db.execute(select(Conductor).where(Conductor.usuario_id == user.usuario_id))).scalar_one_or_none()
    if conductor is None or not conductor.activo:
        raise HTTPException(status_code=403, detail="Su usuario no tiene un perfil de conductor activo")
    return conductor


async def _parada_propia(db: AsyncSession, conductor: Conductor, parada_id: str) -> ParadaRuta:
    parada = (await db.execute(
        select(ParadaRuta).where(ParadaRuta.parada_id == parada_id).options(
            selectinload(ParadaRuta.pedido),
            selectinload(ParadaRuta.ruta).selectinload(Ruta.paradas).selectinload(ParadaRuta.pedido),
            selectinload(ParadaRuta.ruta).selectinload(Ruta.vehiculo),
        )
    )).scalar_one_or_none()
    # Una parada ajena responde igual que una inexistente: no revela datos de otras rutas.
    if parada is None or parada.ruta.conductor_id != conductor.conductor_id:
        raise HTTPException(status_code=404, detail="Parada no encontrada")
    return parada


@router.get("/ruta", response_model=RutaOut)
async def mi_ruta(db: AsyncSession = Depends(get_db), user: Usuario = Depends(_SOLO_CONDUCTOR)):
    """La ruta abierta del conductor con sus paradas y coordenadas (mapa y navegación)."""
    conductor = await _conductor(db, user)
    rutas = await cargar_rutas(
        db, Ruta.conductor_id == conductor.conductor_id, Ruta.estado.in_(("EN_CURSO", "PLANIFICADA")),
    )
    if not rutas:
        raise HTTPException(status_code=404, detail="No tiene una ruta asignada")
    rutas.sort(key=lambda r: r.estado != "EN_CURSO")
    return ruta_out(rutas[0])


async def _duplicada(db: AsyncSession, clave: str | None) -> bool:
    if not clave:
        return False
    return (await db.execute(select(ParadaRuta.parada_id).where(ParadaRuta.clave_sync == clave))).first() is not None


async def _entregar(db: AsyncSession, user: Usuario, parada: ParadaRuta, datos: EntregaIn) -> EntregaOut:
    ruta = parada.ruta
    if ruta.estado != "EN_CURSO":
        raise HTTPException(status_code=409, detail="La ruta todavía no fue iniciada o ya no está en curso")
    if parada.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="La parada ya fue resuelta")
    # RN-007: sin evidencia (foto o firma) la entrega no se registra.
    if not datos.evidencia_tipo or not datos.evidencia:
        raise HTTPException(status_code=422, detail="La entrega exige evidencia: una foto o la firma del receptor (RN-007)")

    momento = utc(datos.momento) or ahora()
    parada.estado = "ENTREGADA"
    parada.entregada_en = momento
    parada.evidencia_tipo = datos.evidencia_tipo
    parada.evidencia = datos.evidencia
    parada.latitud_entrega = datos.latitud
    parada.longitud_entrega = datos.longitud
    parada.clave_sync = datos.clave_sync
    parada.pedido.estado = "ENTREGADO"
    parada.pedido.entregado_en = momento
    notificador = Notificador(db)
    await notificador.avisar(parada.pedido, "ENTREGA", "Su pedido fue entregado.")

    # RN-005: si el retraso acumulado pone en riesgo la ventana de una parada siguiente, se re-optimiza lo que falta.
    reoptimizada = False
    mensaje = "Entrega registrada"
    llegada = utc(parada.llegada_estimada)
    retraso = (momento - llegada).total_seconds() / 60.0 if llegada else 0.0
    if retraso > 0:
        en_riesgo = [
            p for p in ruta.paradas
            if p.estado == "PENDIENTE" and p.llegada_estimada and p.pedido.ventana_fin
            and utc(p.llegada_estimada) + timedelta(minutes=retraso) > utc(p.pedido.ventana_fin)
        ]
        if en_riesgo:
            posicion = (datos.latitud, datos.longitud) if datos.latitud is not None and datos.longitud is not None else None
            await reoptimizar_ruta(
                db, ruta, user, tipo="RETRASO", descripcion=f"Retraso de {retraso:.0f} min", momento=momento,
                posicion=posicion,
            )
            reoptimizada = True
            mensaje = "Entrega registrada; se re-optimizó el resto de la ruta por riesgo de incumplir ventanas"
            for p in en_riesgo:
                if p.estado == "PENDIENTE":
                    await notificador.avisar(
                        p.pedido, "RETRASO", "Su pedido llegará más tarde de lo previsto; se recalculó la hora.",
                        p.llegada_estimada,
                    )
                else:
                    await notificador.avisar(
                        p.pedido, "REPROGRAMACION", "Su pedido no se podrá entregar hoy en su ventana y se reprogramará.",
                    )
    await db.flush()
    return EntregaOut(
        parada_id=parada.parada_id, estado=parada.estado, ruta_completable=all(parada_resuelta(p) for p in ruta.paradas),
        reoptimizada=reoptimizada, mensaje=mensaje,
    )


async def _reprogramar(db: AsyncSession, parada: ParadaRuta, datos: ReprogramarIn) -> EntregaOut:
    ruta = parada.ruta
    if ruta.estado != "EN_CURSO":
        raise HTTPException(status_code=409, detail="La ruta todavía no fue iniciada o ya no está en curso")
    if parada.estado != "PENDIENTE":
        raise HTTPException(status_code=409, detail="La parada ya fue resuelta")
    parada.estado = "REPROGRAMADA"
    parada.motivo = datos.motivo
    parada.clave_sync = datos.clave_sync
    parada.pedido.estado = "PENDIENTE"
    parada.pedido.reprogramaciones = (parada.pedido.reprogramaciones or 0) + 1
    await Notificador(db).avisar(
        parada.pedido, "REPROGRAMACION", f"Su pedido no pudo entregarse y será reprogramado. Motivo: {datos.motivo}",
    )
    await db.flush()
    return EntregaOut(
        parada_id=parada.parada_id, estado=parada.estado, ruta_completable=all(parada_resuelta(p) for p in ruta.paradas),
        mensaje="Pedido reprogramado",
    )


@router.post("/paradas/{parada_id}/entregar", response_model=EntregaOut)
async def entregar(
    parada_id: str, payload: EntregaIn, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_SOLO_CONDUCTOR),
):
    """Confirma una entrega con su evidencia y ubicación. Repetir la misma `clave_sync` no la duplica."""
    conductor = await _conductor(db, user)
    if await _duplicada(db, payload.clave_sync):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Acción ya sincronizada (clave_sync repetida)")
    parada = await _parada_propia(db, conductor, parada_id)
    return await _entregar(db, user, parada, payload)


@router.post("/paradas/{parada_id}/reprogramar", response_model=EntregaOut)
async def reprogramar(
    parada_id: str, payload: ReprogramarIn, db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(_SOLO_CONDUCTOR),
):
    """Reprograma una parada que no pudo entregarse (cliente ausente, dirección errónea, etc.)."""
    conductor = await _conductor(db, user)
    if await _duplicada(db, payload.clave_sync):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Acción ya sincronizada (clave_sync repetida)")
    parada = await _parada_propia(db, conductor, parada_id)
    return await _reprogramar(db, parada, payload)


@router.post("/sync", response_model=SyncOut)
async def sincronizar(payload: SyncIn, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_SOLO_CONDUCTOR)):
    """
    Aplica en orden las acciones guardadas sin conexión. Cada una es independiente: una rechazada no detiene las demás, y
    una ya aplicada (misma `clave_sync`) se informa como DUPLICADA sin repetirla.
    """
    conductor = await _conductor(db, user)
    resultados: list[ResultadoSync] = []
    for accion in payload.acciones:
        if await _duplicada(db, accion.clave_sync):
            resultados.append(ResultadoSync(clave_sync=accion.clave_sync, estado="DUPLICADA", detalle="Ya aplicada"))
            continue
        try:
            parada = await _parada_propia(db, conductor, accion.parada_id)
            if accion.tipo == "ENTREGA":
                await _entregar(db, user, parada, EntregaIn(
                    evidencia_tipo=accion.evidencia_tipo, evidencia=accion.evidencia, latitud=accion.latitud,
                    longitud=accion.longitud, momento=accion.momento, clave_sync=accion.clave_sync,
                ))
            else:
                if not accion.motivo or len(accion.motivo) < 3:
                    raise HTTPException(status_code=422, detail="La reprogramación exige un motivo")
                await _reprogramar(db, parada, ReprogramarIn(
                    motivo=accion.motivo, momento=accion.momento, clave_sync=accion.clave_sync,
                ))
            resultados.append(ResultadoSync(clave_sync=accion.clave_sync, estado="APLICADA"))
        except HTTPException as exc:
            resultados.append(ResultadoSync(clave_sync=accion.clave_sync, estado="RECHAZADA", detalle=str(exc.detail)))
    return SyncOut(
        resultados=resultados,
        aplicadas=sum(r.estado == "APLICADA" for r in resultados),
        duplicadas=sum(r.estado == "DUPLICADA" for r in resultados),
        rechazadas=sum(r.estado == "RECHAZADA" for r in resultados),
    )


def _distancia_a_tramo_km(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia del punto `p` al segmento `a`–`b`, con proyección plana local (suficiente a escala urbana)."""
    k = math.radians(1) * RADIO_TIERRA_KM
    cos_lat = math.cos(math.radians(p[0]))

    def plano(q: tuple[float, float]) -> tuple[float, float]:
        return (q[1] - p[1]) * k * cos_lat, (q[0] - p[0]) * k

    ax, ay = plano(a)
    bx, by = plano(b)
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    t = 0.0 if largo2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / largo2))
    return math.hypot(ax + t * dx, ay + t * dy)


@router.post("/ubicacion", response_model=UbicacionOut)
async def reportar_ubicacion(
    payload: UbicacionIn, db: AsyncSession = Depends(get_db), user: Usuario = Depends(_SOLO_CONDUCTOR),
):
    """Compara la posición GPS con el trazado planificado; si se aleja más de 500 m re-optimiza desde donde está (RF-004)."""
    conductor = await _conductor(db, user)
    rutas = await cargar_rutas(db, Ruta.conductor_id == conductor.conductor_id, Ruta.estado == "EN_CURSO")
    if not rutas:
        raise HTTPException(status_code=404, detail="No tiene una ruta en curso")
    ruta = rutas[0]
    deposito = (settings.DEPOSITO_LATITUD, settings.DEPOSITO_LONGITUD)
    hechas = [p for p in ruta.paradas if p.estado == "ENTREGADA"]
    origen = (float(hechas[-1].pedido.latitud), float(hechas[-1].pedido.longitud)) if hechas else deposito
    pendientes = sorted((p for p in ruta.paradas if p.estado == "PENDIENTE"), key=lambda x: x.orden)
    trazado = [origen] + [(float(p.pedido.latitud), float(p.pedido.longitud)) for p in pendientes] + [deposito]
    posicion = (payload.latitud, payload.longitud)
    desviacion = min(_distancia_a_tramo_km(posicion, a, b) for a, b in zip(trazado, trazado[1:], strict=False))
    desviado = desviacion > UMBRAL_DESVIO_KM
    if not desviado or not pendientes:
        return UbicacionOut(
            desviado=False, desviacion_km=round(desviacion, 3), umbral_km=UMBRAL_DESVIO_KM, mensaje="En ruta",
        )
    resultado = await reoptimizar_ruta(
        db, ruta, user, tipo="DESVIO", descripcion=f"Desvío de {desviacion * 1000:.0f} m", posicion=posicion,
    )
    return UbicacionOut(
        desviado=True, desviacion_km=round(desviacion, 3), umbral_km=UMBRAL_DESVIO_KM, reoptimizada=True,
        mensaje=f"Desvío de {desviacion * 1000:.0f} m detectado. {resultado.sugerencia}",
    )
