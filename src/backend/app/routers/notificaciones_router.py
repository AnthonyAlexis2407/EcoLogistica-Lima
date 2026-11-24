"""
Router de Notificaciones — RF-009 (portal para clientes) y RN-010 (aislamiento por bodega).

Cada usuario solo ve los avisos dirigidos a su propia cuenta. Los operadores ven además los que quedaron como
NO_ENTREGADA (cliente sin canal de contacto) para llamarlo por teléfono.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.models import Notificacion, Usuario
from app.schemas import MensajeResponse, NotificacionOut

router = APIRouter(prefix="/api/notificaciones", tags=["Notificaciones (RF-009)"])


@router.get("/", response_model=list[NotificacionOut])
async def mis_notificaciones(
    response: Response,
    solo_no_leidas: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    """Avisos del usuario autenticado, los más recientes primero."""
    filtros = [Notificacion.usuario_id == user.usuario_id]
    if solo_no_leidas:
        filtros.append(Notificacion.leida.is_(False))
    total_no_leidas = await db.scalar(
        select(func.count()).select_from(Notificacion).where(
            Notificacion.usuario_id == user.usuario_id, Notificacion.leida.is_(False),
        )
    )
    response.headers["X-Unread-Count"] = str(total_no_leidas or 0)
    filas = await db.execute(
        select(Notificacion).where(*filtros).order_by(Notificacion.creado_en.desc()).limit(limit)
    )
    return filas.scalars().all()


@router.get("/pendientes-de-contacto", response_model=list[NotificacionOut])
async def pendientes_de_contacto(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """Avisos que no pudieron enviarse porque el cliente no tiene canal: el operador debe contactarlo (RF-009)."""
    filas = await db.execute(
        select(Notificacion).where(Notificacion.estado_envio == "NO_ENTREGADA")
        .order_by(Notificacion.creado_en.desc()).limit(200)
    )
    return filas.scalars().all()


@router.put("/{notificacion_id}/leida", response_model=MensajeResponse)
async def marcar_leida(
    notificacion_id: str, db: AsyncSession = Depends(get_db), user: Usuario = Depends(get_current_user),
):
    notificacion = await db.get(Notificacion, notificacion_id)
    # Un aviso de otra cuenta responde igual que uno inexistente (RN-010).
    if notificacion is None or notificacion.usuario_id != user.usuario_id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notificacion.leida = True
    await db.flush()
    return MensajeResponse(mensaje="Notificación marcada como leída")
