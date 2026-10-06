"""
Router de Autenticación — EN-002.
Endpoints: registro de usuario, login con JWT, perfil del usuario actual.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    get_optional_user,
    hash_password,
    is_account_locked,
    register_failed_attempt,
    reset_login_attempts,
    verify_password,
)
from app.database import get_db
from app.models import Usuario
from app.schemas import LoginRequest, Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    actor: Usuario | None = Depends(get_optional_user),
):
    """
    Registra un nuevo usuario con contraseña hasheada (EN-008).

    DEF-003: el registro público solo admite el rol BODEGA; crear usuarios con
    cualquier otro rol exige un ADMIN_FLOTA autenticado (Documento 08).
    """
    es_administrador = actor is not None and actor.rol in ("ADMIN_FLOTA", "ADMINISTRADOR")
    if payload.rol != "BODEGA" and not es_administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Solo un administrador de flota puede crear usuarios con el rol {payload.rol}. "
                   "El registro público únicamente permite el rol BODEGA.",
        )
    # Verificar email único
    exists = await db.execute(select(Usuario).where(Usuario.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo electrónico",
        )

    user = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica un usuario y retorna JWT.
    Implementa bloqueo por intentos fallidos (EN-002 / RNF-002):
    3 intentos fallidos → bloqueo 15 minutos.
    """
    result = await db.execute(select(Usuario).where(Usuario.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Verificar lockout
    if is_account_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta bloqueada por múltiples intentos fallidos. Intente nuevamente en {user.locked_until}",
        )

    # Verificar contraseña
    if not verify_password(payload.password, user.password_hash):
        await register_failed_attempt(user, db)
        # Persistir el contador ANTES de lanzar la excepción: get_db hace rollback
        # ante cualquier excepción y, sin este commit, el bloqueo nunca se acumulaba.
        await db.commit()
        remaining = max(0, 3 - user.login_attempts)
        raise HTTPException(
            status_code=401,
            detail=f"Credenciales inválidas. Intentos restantes: {remaining}",
        )

    # Login exitoso → resetear contador
    await reset_login_attempts(user, db)

    token = create_access_token(data={"sub": user.usuario_id, "rol": user.rol})
    return Token(access_token=token, usuario=UsuarioOut.model_validate(user))


@router.get("/me", response_model=UsuarioOut)
async def me(user: Usuario = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado."""
    return user
