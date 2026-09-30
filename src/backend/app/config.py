"""
Configuración centralizada del backend EcoLogística Lima.
Carga variables de entorno desde .env; usa valores por defecto seguros para desarrollo.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Aplicación ---
    APP_NAME: str = "EcoLogística Lima API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # --- Base de datos (SQLite por defecto para desarrollo) ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./ecologistica.db"

    # --- JWT / Autenticación (EN-002) ---
    SECRET_KEY: str = "dev-secret-key-cambiar-en-produccion-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Seguridad: intentos fallidos de login (EN-002 / RNF-002) ---
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_MINUTES: int = 15

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
