"""
Router de Vehículos — US-001: Registrar y administrar vehículos de la flota.

RBAC (Documento 08):
- ADMIN_FLOTA: CRUD completo
- OPERADOR: solo lectura
- AUDITOR: solo lectura
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.database import get_db
from app.models import Usuario, Vehiculo
from app.schemas import MensajeResponse, VehiculoCreate, VehiculoOut, VehiculoUpdate

router = APIRouter(prefix="/api/vehiculos", tags=["Vehículos (US-001)"])


@router.get("/", response_model=list[VehiculoOut])
async def listar_vehiculos(
    estado: str | None = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Lista todos los vehículos del catálogo con paginación y filtro opcional."""
    query = select(Vehiculo)
    if estado:
        query = query.where(Vehiculo.estado == estado.upper())
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def contar_vehiculos(
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Retorna el total de vehículos por estado."""
    result = await db.execute(
        select(Vehiculo.estado, func.count(Vehiculo.vehiculo_id)).group_by(Vehiculo.estado)
    )
    counts = {row[0]: row[1] for row in result.all()}
    counts["TOTAL"] = sum(counts.values())
    return counts


@router.get("/{vehiculo_id}", response_model=VehiculoOut)
async def obtener_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA", "OPERADOR", "AUDITOR")),
):
    """Obtiene un vehículo por su ID."""
    result = await db.execute(select(Vehiculo).where(Vehiculo.vehiculo_id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo


@router.post("/", response_model=VehiculoOut, status_code=status.HTTP_201_CREATED)
async def crear_vehiculo(
    payload: VehiculoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA")),
):
    """
    Registra un vehículo nuevo.
    Valida placa única (RF-001: rechazo por duplicidad).
    """
    # Verificar placa duplicada
    exists = await db.execute(select(Vehiculo).where(Vehiculo.placa == payload.placa))
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un vehículo con la placa '{payload.placa}'. Registro rechazado por duplicidad.",
        )

    vehiculo = Vehiculo(**payload.model_dump())
    db.add(vehiculo)
    await db.flush()
    await db.refresh(vehiculo)
    return vehiculo


@router.put("/{vehiculo_id}", response_model=VehiculoOut)
async def actualizar_vehiculo(
    vehiculo_id: str,
    payload: VehiculoUpdate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA")),
):
    """Actualiza los campos de un vehículo existente."""
    result = await db.execute(select(Vehiculo).where(Vehiculo.vehiculo_id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    update_data = payload.model_dump(exclude_unset=True)

    # Si cambia placa, verificar unicidad
    if "placa" in update_data:
        dup = await db.execute(
            select(Vehiculo).where(Vehiculo.placa == update_data["placa"], Vehiculo.vehiculo_id != vehiculo_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe otro vehículo con la placa '{update_data['placa']}'.",
            )

    for key, value in update_data.items():
        setattr(vehiculo, key, value)

    db.add(vehiculo)
    await db.flush()
    await db.refresh(vehiculo)
    return vehiculo


@router.delete("/{vehiculo_id}", response_model=MensajeResponse)
async def dar_baja_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_roles("ADMIN_FLOTA")),
):
    """
    Da de baja lógica un vehículo (cambia estado a FUERA_DE_SERVICIO).
    No elimina físicamente el registro para preservar historial.
    """
    result = await db.execute(select(Vehiculo).where(Vehiculo.vehiculo_id == vehiculo_id))
    vehiculo = result.scalar_one_or_none()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    vehiculo.estado = "FUERA_DE_SERVICIO"
    db.add(vehiculo)
    await db.flush()
    return MensajeResponse(mensaje=f"Vehículo {vehiculo.placa} dado de baja exitosamente")
