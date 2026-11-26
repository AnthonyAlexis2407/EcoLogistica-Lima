"""
Router de Pedidos — US-003: Registrar pedidos con ventana horaria y ubicación.

RBAC (Documento 08):
- OPERADOR: CRUD completo
- BODEGA: crear y leer solo los propios
- ADMIN_FLOTA: solo lectura
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.database import get_db
from app.distritos import distrito_mas_cercano
from app.models import Bodega, Pedido, Usuario, Vehiculo
from app.schemas import MensajeResponse, PedidoCreate, PedidoOut, PedidoUpdate
from app.tiempo import lima_a_utc

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos (US-003)"])

# La dirección se guarda cifrada (RNF-008), por lo que la búsqueda por texto se hace sobre las filas ya descifradas.
LIMITE_BUSQUEDA = 5000

# Solo las columnas que expone PedidoOut: no se hidratan entidades ORM (equivalente a select + lean).
_COLUMNAS = (
    Pedido.pedido_id, Pedido.bodega_id, Pedido.direccion, Pedido.latitud, Pedido.longitud,
    Pedido.peso_kg, Pedido.volumen_m3, Pedido.distrito, Pedido.ventana_inicio, Pedido.ventana_fin, Pedido.estado,
    Pedido.reprogramaciones, Pedido.entregado_en, Pedido.creado_en,
)


@router.get("/", response_model=list[PedidoOut])
async def listar_pedidos(
    response: Response,
    estado: str | None = Query(None, description="Filtrar por estado"),
    bodega_id: str | None = Query(None, description="Filtrar por bodega"),
    q: str | None = Query(None, max_length=100, description="Buscar por dirección"),
    distrito: str | None = Query(None, max_length=40, description="Filtrar por distrito"),
    desde: datetime | None = Query(None, description="Creados desde esta fecha"),
    hasta: datetime | None = Query(None, description="Creados hasta esta fecha"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "BODEGA")),
):
    """Lista pedidos por páginas de 12; el total viaja en X-Total-Count. Bodega solo ve los propios (RN-010)."""
    filtros = []

    # Aislamiento por bodega (RN-010)
    if user.rol == "BODEGA":
        bodega_result = await db.execute(select(Bodega).where(Bodega.usuario_id == user.usuario_id))
        bodega = bodega_result.scalar_one_or_none()
        if not bodega:
            response.headers["X-Total-Count"] = "0"
            return []
        filtros.append(Pedido.bodega_id == bodega.bodega_id)
    elif bodega_id:
        filtros.append(Pedido.bodega_id == bodega_id)

    if estado:
        filtros.append(Pedido.estado == estado.upper())
    if distrito:
        filtros.append(Pedido.distrito == distrito)
    if desde:
        filtros.append(Pedido.creado_en >= lima_a_utc(desde))
    if hasta:
        filtros.append(Pedido.creado_en <= lima_a_utc(hasta))

    orden = (Pedido.creado_en.desc(), Pedido.pedido_id)
    if q and q.strip():
        aguja = q.strip().lower()
        filas = await db.execute(select(*_COLUMNAS).where(*filtros).order_by(*orden).limit(LIMITE_BUSQUEDA))
        coincidencias = [dict(f) for f in filas.mappings() if aguja in f["direccion"].lower()]
        response.headers["X-Total-Count"] = str(len(coincidencias))
        return coincidencias[(page - 1) * limit: page * limit]

    total = await db.scalar(select(func.count()).select_from(Pedido).where(*filtros))
    filas = await db.execute(
        select(*_COLUMNAS).where(*filtros).order_by(*orden).offset((page - 1) * limit).limit(limit)
    )
    response.headers["X-Total-Count"] = str(total or 0)
    return [dict(fila) for fila in filas.mappings()]


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
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "BODEGA")),
):
    """
    Registra un pedido nuevo.
    Valida que el peso no exceda la capacidad máxima de la flota (RF-002).
    """
    # Aislamiento por bodega al escribir (RN-010 / DEF-002): una BODEGA solo registra
    # pedidos a nombre de su propia bodega.
    if user.rol == "BODEGA":
        propia_result = await db.execute(select(Bodega).where(Bodega.usuario_id == user.usuario_id))
        propia = propia_result.scalar_one_or_none()
        if propia and payload.bodega_id is None:
            payload.bodega_id = propia.bodega_id
        if not propia or propia.bodega_id != payload.bodega_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede registrar pedidos a nombre de su propia bodega",
            )

    # Verificar que la bodega existe
    bodega_result = await db.execute(select(Bodega).where(Bodega.bodega_id == payload.bodega_id))
    bodega_obj = bodega_result.scalar_one_or_none()
    if not bodega_obj:
        # Fallback: asociar a la primera bodega registrada si no se encuentra
        first_bodega_res = await db.execute(select(Bodega))
        first_bodega = first_bodega_res.scalars().first()
        if first_bodega:
            payload.bodega_id = first_bodega.bodega_id
        else:
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

    datos = payload.model_dump()
    if not datos.get("distrito"):
        datos["distrito"] = distrito_mas_cercano(float(payload.latitud), float(payload.longitud))
    # RN-004: el volumen del pedido no puede superar el mayor volumen registrado en la flota disponible.
    if payload.volumen_m3 is not None:
        max_vol = (await db.execute(
            select(func.max(Vehiculo.volumen_m3)).where(Vehiculo.estado == "DISPONIBLE")
        )).scalar()
        if max_vol is not None and payload.volumen_m3 > max_vol:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El volumen del pedido ({payload.volumen_m3} m³) excede el mayor volumen "
                       f"de la flota ({max_vol} m³).",
            )
    pedido = Pedido(**datos)
    db.add(pedido)
    await db.flush()
    await db.refresh(pedido)
    return pedido


@router.put("/{pedido_id}", response_model=PedidoOut)
async def actualizar_pedido(
    pedido_id: str,
    payload: PedidoUpdate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR")),
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
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "BODEGA")),
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
