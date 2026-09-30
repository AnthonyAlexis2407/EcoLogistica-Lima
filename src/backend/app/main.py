"""
EcoLogística Lima — Punto de entrada de la API REST (FastAPI).
Sprint 1: Autenticación (EN-002), Cifrado (EN-008), Vehículos (US-001), Pedidos (US-003).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth_router, vehiculos_router, pedidos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la BD al arrancar y cierra recursos al terminar."""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST del sistema EcoLogística Lima — Optimizador de Rutas Sostenibles "
        "para DistriRápido S.A.C. Sprint 1: Autenticación, Gestión de Flota y Pedidos."
    ),
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(vehiculos_router.router)
app.include_router(pedidos_router.router)


@app.get("/api/health", tags=["Sistema"])
async def health_check():
    """Endpoint de healthcheck para verificar que el backend está operativo."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
