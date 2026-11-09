"""
EcoLogística Lima — Punto de entrada de la API REST (FastAPI).
Hardening OWASP (EN-002), Cifrado (EN-008), Vehículos (US-001), Pedidos (US-003).
Sprint 3: configuración endurecida (OWASP A02), cabeceras de seguridad y CORS acotado.
"""

import logging
from contextlib import asynccontextmanager

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.rendimiento import montar_frontend, politica_http
from app.routers import auth_router, vehiculos_router, pedidos_router


_PRODUCCION = settings.ENVIRONMENT == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la BD al arrancar y cierra recursos al terminar."""
    if settings.SECRET_KEY.startswith("dev-secret-key"):
        if settings.ENVIRONMENT == "production":
            raise RuntimeError("SECRET_KEY por defecto no permitida en producción: defínala en el entorno")
        logging.getLogger("ecologistica.security").warning(
            "SECRET_KEY usa el valor por defecto de desarrollo; defina una clave propia en .env antes de desplegar"
        )
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST del sistema EcoLogística Lima — Optimizador de Rutas Sostenibles "
        "para DistriRápido S.A.C. Hardening de Seguridad OWASP, Gestión de Flota y Pedidos."
    ),
    lifespan=lifespan,
    docs_url=None if _PRODUCCION else "/docs",
    redoc_url=None if _PRODUCCION else "/redoc",
    openapi_url=None if _PRODUCCION else "/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "If-None-Match"],
    expose_headers=["X-Total-Count", "ETag"],
)

# ── Rendimiento y seguridad HTTP (Informe Green IT) ──────────────────
# Orden: politica_http (ETag, caché, cabeceras) queda dentro; la compresión Brotli/Gzip, fuera,
# para comprimir el cuerpo final. Solo se comprimen respuestas de 1 KB o más.
app.middleware("http")(politica_http)
app.add_middleware(BrotliMiddleware, quality=5, minimum_size=1000, gzip_fallback=True)

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


# El frontend compilado se registra al final: su ruta comodín no debe tapar la API.
montar_frontend(app, settings.FRONTEND_DIST)
