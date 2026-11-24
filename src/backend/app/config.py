"""
Configuración centralizada del backend EcoLogística Lima.
Carga variables de entorno desde .env; usa valores por defecto seguros para desarrollo.
"""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Aplicación ---
    APP_NAME: str = "EcoLogística Lima API"
    APP_VERSION: str = "4.0.0"
    ENVIRONMENT: str = "development"  # "production" exige SECRET_KEY propia y oculta /docs
    # True carga usuarios, flota y pedidos de ejemplo al arrancar (idempotente). Solo para entornos de
    # demostración y pruebas: crea cuentas con contraseñas de prueba conocidas (ver app/seed.py).
    SEED_DEMO_DATA: bool = False
    DEBUG: bool = False  # True activa el eco de SQL; actívelo solo en desarrollo (.env)

    # --- Base de datos: SQLite en desarrollo y PostgreSQL en producción (postgres:// y postgresql:// se normalizan) ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./ecologistica.db"

    # --- JWT / Autenticación (EN-002) ---
    SECRET_KEY: str = "dev-secret-key-cambiar-en-produccion-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Cifrado de datos personales en reposo (RNF-008): clave propia; si falta se deriva de SECRET_KEY ---
    DATA_ENCRYPTION_KEY: str = ""

    # --- Seguridad: intentos fallidos de login (EN-002 / RNF-002) ---
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_MINUTES: int = 15

    # --- Motor de rutas (RF-003): depósito de salida y límite de cálculo por debajo del SLA de 45 s (RNF-001) ---
    DEPOSITO_LATITUD: float = -12.0464
    DEPOSITO_LONGITUD: float = -77.0428
    OPTIMIZADOR_LIMITE_SEGUNDOS: float = 40.0

    # --- Notificaciones (RF-009): "portal" registra y muestra en el portal; "smtp" además envía correos ---
    NOTIFICACIONES_MODO: str = "portal"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USUARIO: str = ""
    SMTP_CLAVE: str = ""
    SMTP_REMITENTE: str = "notificaciones@ecologistica.pe"

    # --- Frontend compilado (npm run build): si existe, la API lo sirve desde el mismo origen ---
    FRONTEND_DIST: Path = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @field_validator("DATABASE_URL")
    @classmethod
    def normalizar_url(cls, valor: str) -> str:
        """Render entrega `postgres://` o `postgresql://`; SQLAlchemy asíncrono necesita el controlador asyncpg."""
        for prefijo in ("postgres://", "postgresql://"):
            if valor.startswith(prefijo):
                return "postgresql+asyncpg://" + valor[len(prefijo):]
        return valor


settings = Settings()
