"""
Router de Pedidos — US-003: Registrar pedidos con ventana horaria y ubicación.

RBAC (Documento 08):
- OPERADOR: CRUD completo
- BODEGA: crear y leer solo los propios
- ADMIN_FLOTA: solo lectura
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.database import get_db
from app.models import Bodega, Pedido, Usuario, Vehiculo
from app.schemas import MensajeResponse, PedidoCreate, PedidoOut, PedidoUpdate

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos (US-003)"])


@router.get("/", response_model=list[PedidoOut])
async def listar_pedidos(
    estado: str | None = Query(None, description="Filtrar por estado"),
    bodega_id: str | None = Query(None, description="Filtrar por bodega"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "BODEGA")),
):
    """Lista pedidos con filtros opcionales. Bodega solo ve los propios (RN-010)."""
    query = select(Pedido)

    # Aislamiento por bodega (RN-010)
    if user.rol == "BODEGA":
        bodega_result = await db.execute(select(Bodega).where(Bodega.usuario_id == user.usuario_id))
        bodega = bodega_result.scalar_one_or_none()
        if not bodega:
            return []
        query = query.where(Pedido.bodega_id == bodega.bodega_id)
    elif bodega_id:
        query = query.where(Pedido.bodega_id == bodega_id)

    if estado:
        query = query.where(Pedido.estado == estado.upper())

    query = query.order_by(Pedido.creado_en.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def contar_pedidos(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
):
    """Retorna el total de pedidos por estado."""
    result = await db.execute(
        select(Pedido.estado, func.count(Pedido.pedido_id)).group_by(Pedido.estado)
    )
    counts = {row[0]: row[1] for row in result.all()}
    counts["TOTAL"] = sum(counts.values())
    return counts


@router.get("/{pedido_id}", response_model=PedidoOut)
async def obtener_pedido(
    pedido_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "BODEGA")),
):
    """Obtiene un pedido por su ID."""
    result = await db.execute(select(Pedido).where(Pedido.pedido_id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Bodega solo puede ver sus propios pedidos
    if user.rol == "BODEGA":
        bodega_result = await db.execute(select(Bodega).where(Bodega.usuario_id == user.usuario_id))
        bodega = bodega_result.scalar_one_or_none()
        if not bodega or pedido.bodega_id != bodega.bodega_id:
            raise HTTPException(status_code=403, detail="No tiene acceso a este pedido")

    return pedido


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    payload: PedidoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("OPERADOR", "BODEGA")),
):
    """
    Registra un pedido nuevo.
    Valida que el peso no exceda la capacidad máxima de la flota (RF-002).
    """
    # Verificar que la bodega existe
    bodega_result = await db.execute(select(Bodega).where(Bodega.bodega_id == payload.bodega_id))
    if not bodega_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bodega no encontrada")

    # Validar capacidad vehicular (RF-002: ruta infeliz)
    max_cap_result = await db.execute(
        select(func.max(Vehiculo.capacidad_kg)).where(Vehiculo.estado == "DISPONIBLE")
    )
    max_capacidad = max_cap_result.scalar()
    if max_capacidad is not None and payload.peso_kg > max_capacidad:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El peso del pedido ({payload.peso_kg} kg) excede la capacidad máxima "
                   f"de cualquier vehículo disponible en la flota ({max_capacidad} kg). "
                   f"Registro rechazado por incompatibilidad de capacidad.",
        )

    pedido = Pedido(**payload.model_dump())
    db.add(pedido)
    await db.flush()
    await db.refresh(pedido)
    return pedido


@router.put("/{pedido_id}", response_model=PedidoOut)
async def actualizar_pedido(
    pedido_id: str,
    payload: PedidoUpdate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("OPERADOR")),
):
    """Actualiza un pedido existente."""
    result = await db.execute(select(Pedido).where(Pedido.pedido_id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pedido, key, value)

    db.add(pedido)
    await db.flush()
    await db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}", response_model=MensajeResponse)
async def cancelar_pedido(
    pedido_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("OPERADOR")),
):
    """Cancela un pedido (cambio de estado lógico, no eliminación física)."""
    result = await db.execute(select(Pedido).where(Pedido.pedido_id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if pedido.estado == "CANCELADO":
        raise HTTPException(status_code=400, detail="El pedido ya se encuentra cancelado")

    pedido.estado = "CANCELADO"
    db.add(pedido)
    await db.flush()
    return MensajeResponse(mensaje=f"Pedido {pedido_id} cancelado exitosamente")
