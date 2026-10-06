"""
Módulo de autenticación y seguridad — EN-002 (Hardening OWASP) + EN-008 (Cifrado).

Implementa:
- Hashing de contraseñas con bcrypt (EN-008)
- JWT con expiración configurable (EN-002)
- Bloqueo de cuenta por intentos fallidos (RNF-002: 3 intentos → 15 min lockout)
- Dependency de FastAPI para proteger endpoints por rol (RBAC)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# Variante que no exige token: permite endpoints públicos con comportamiento distinto si hay sesión.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# ── Hashing (EN-008) ──────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    """Genera hash bcrypt de una contraseña en texto plano."""
    pwd_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


get_password_hash = hash_password


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica contraseña contra hash bcrypt almacenado."""
    pwd_bytes = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))


# ── JWT (EN-002) ──────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependency: usuario autenticado ──────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Extrae y valida el usuario del JWT."""
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido")

    result = await db.execute(select(Usuario).where(Usuario.usuario_id == user_id))
    user = result.scalar_one_or_none()
    if user is None or user.estado != "ACTIVO":
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[Usuario]:
    """Devuelve el usuario autenticado o None si no hay token (token inválido → 401)."""
    if not token:
        return None
    return await get_current_user(token=token, db=db)


# ── Dependency factory: verificar rol (RBAC — Documento 08) ──────────
def require_roles(*allowed_roles: str):
    """
    Devuelve un dependency que verifica que el usuario autenticado
    tenga uno de los roles permitidos (o el rol de ADMINISTRADOR).
    """
    async def role_checker(user: Usuario = Depends(get_current_user)) -> Usuario:
        if user.rol == "ADMINISTRADOR" or user.rol in allowed_roles:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acceso denegado. Roles permitidos: {', '.join(allowed_roles)}",
        )
    return role_checker


# ── Lógica de lockout (EN-002 — RNF-002) ─────────────────────────────
def is_account_locked(user: Usuario) -> bool:
    """Verifica si la cuenta está bloqueada por intentos fallidos."""
    locked_until = user.locked_until
    if locked_until is None:
        return False
    # SQLite (BD de desarrollo) devuelve datetimes sin zona horaria: se asumen UTC.
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return locked_until > datetime.now(timezone.utc)


async def register_failed_attempt(user: Usuario, db: AsyncSession) -> None:
    """Incrementa contador de intentos y bloquea si alcanza el umbral."""
    user.login_attempts += 1
    if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_MINUTES)
    db.add(user)
    await db.flush()


async def reset_login_attempts(user: Usuario, db: AsyncSession) -> None:
    """Resetea el contador tras login exitoso."""
    user.login_attempts = 0
    user.locked_until = None
    db.add(user)
    await db.flush()
