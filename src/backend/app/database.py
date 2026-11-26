"""
Configuración del motor SQLAlchemy asíncrono y session factory.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_es_sqlite = "sqlite" in settings.DATABASE_URL
_opciones = (
    {"connect_args": {"check_same_thread": False}}
    # PostgreSQL: conexiones verificadas antes de usarse (recuperación tras una conmutación, RNF-003).
    if _es_sqlite else {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 10}
)

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, **_opciones)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""
    pass


async def get_db():
    """Dependency que provee una sesión de BD por request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Crea todas las tablas al iniciar la aplicación (solo desarrollo)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
