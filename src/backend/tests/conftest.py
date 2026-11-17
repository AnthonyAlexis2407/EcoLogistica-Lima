"""
Fixtures compartidos de las pruebas del backend.

`api` levanta una base SQLite en memoria con la dependencia `get_db` REAL (con su commit/rollback) y
usuarios con los roles reales del seed (ADMIN_FLOTA, OPERADOR y BODEGA).
"""

from types import SimpleNamespace

import pytest_asyncio
from app import database
from app.auth import hash_password
from app.database import Base
from app.main import app
from app.models import Bodega, Usuario
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from tests.utilidades import PASSWORDS


@pytest_asyncio.fixture
async def api(monkeypatch):
    """BD SQLite en memoria + get_db real (commit/rollback) + usuarios con roles reales."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr(database, "AsyncSessionLocal", session_factory)

    bodegas = {}
    async with session_factory() as s:
        for email, rol, nombre in [
            ("admin@test.pe", "ADMIN_FLOTA", "Admin Flota"),
            ("operador@test.pe", "OPERADOR", "Operador Logístico"),
            ("bodega.a@test.pe", "BODEGA", "Bodega A"),
            ("bodega.b@test.pe", "BODEGA", "Bodega B"),
        ]:
            u = Usuario(
                nombre=nombre, email=email, rol=rol, estado="ACTIVO",
                password_hash=hash_password(PASSWORDS[email]),
            )
            s.add(u)
            await s.flush()
            if rol == "BODEGA":
                b = Bodega(
                    usuario_id=u.usuario_id, razon_social=nombre,
                    direccion_referencial="Av. Próceres de la Independencia, SJL",
                    latitud=-12.0, longitud=-77.0,
                )
                s.add(b)
                await s.flush()
                bodegas[email] = b.bodega_id
        await s.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield SimpleNamespace(
            client=client, bodega_a=bodegas["bodega.a@test.pe"], bodega_b=bodegas["bodega.b@test.pe"]
        )
    await engine.dispose()
