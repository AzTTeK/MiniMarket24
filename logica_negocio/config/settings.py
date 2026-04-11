"""
DEMAND-24 — Configuración Centralizada

Punto único de acceso a todas las variables de entorno y constantes
del sistema. Ningún módulo debe leer .env directamente; todo pasa por aquí.

Uso:
    from backend.config.settings import settings
    print(settings.SUPABASE_URL)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    """Obtiene una variable de entorno con validación."""
    value = os.getenv(key, default)
    if required and not value:
        raise EnvironmentError(
            f"Variable de entorno requerida '{key}' no está definida. "
            f"Revisa tu archivo .env"
        )
    return value or ""


def _get_env_int(key: str, default: int) -> int:
    """Obtiene una variable de entorno como entero."""
    raw = os.getenv(key, str(default))
    try:
        return int(raw)
    except ValueError:
        raise EnvironmentError(
            f"Variable '{key}' debe ser un entero, se recibió: '{raw}'"
        )


def _get_env_float(key: str, default: float) -> float:
    """Obtiene una variable de entorno como flotante."""
    raw = os.getenv(key, str(default))
    try:
        return float(raw)
    except ValueError:
        raise EnvironmentError(
            f"Variable '{key}' debe ser un número, se recibió: '{raw}'"
        )


def _get_env_list(key: str, default: str = "") -> list[str]:
    """Obtiene una variable de entorno como lista separada por comas."""
    raw = os.getenv(key, default)
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Obtiene una variable de entorno como booleano."""
    raw = os.getenv(key, str(default)).lower()
    return raw in ("true", "1", "yes", "si")


@dataclass(frozen=True)
class Settings:
    """Configuración inmutable del sistema DEMAND-24."""

    # --- Supabase ---
    SUPABASE_URL: str = field(
        default_factory=lambda: _get_env("SUPABASE_URL", required=False)
    )
    SUPABASE_ANON_KEY: str = field(
        default_factory=lambda: _get_env("SUPABASE_ANON_KEY", required=False)
    )
    SUPABASE_SERVICE_ROLE_KEY: str = field(
        default_factory=lambda: _get_env("SUPABASE_SERVICE_ROLE_KEY", required=False)
    )

    # --- Base de datos (conexión directa) ---
    DATABASE_URL: str = field(
        default_factory=lambda: _get_env("DATABASE_URL", default="")
    )

    # --- MLflow ---
    MLFLOW_TRACKING_URI: str = field(
        default_factory=lambda: _get_env("MLFLOW_TRACKING_URI", default="http://localhost:5000")
    )

    # --- Configuración del Piloto ---
    PILOT_SKU_IDS: list[str] = field(
        default_factory=lambda: _get_env_list("PILOT_SKU_IDS", "101,102,103,104,105")
    )
    MIN_WEEKS_HISTORY: int = field(
        default_factory=lambda: _get_env_int("MIN_WEEKS_HISTORY", 12)
    )
    MAPE_LOW_CONFIDENCE_THRESHOLD: float = field(
        default_factory=lambda: _get_env_float("MAPE_LOW_CONFIDENCE_THRESHOLD", 25.0)
    )
    ETL_SCHEDULE_CRON: str = field(
        default_factory=lambda: _get_env("ETL_SCHEDULE_CRON", default="0 5 * * 1")
    )

    # --- App ---
    APP_ENV: str = field(
        default_factory=lambda: _get_env("APP_ENV", default="development")
    )
    APP_DEBUG: bool = field(
        default_factory=lambda: _get_env_bool("APP_DEBUG", default=True)
    )
    APP_PORT: int = field(
        default_factory=lambda: _get_env_int("APP_PORT", 8000)
    )

    # --- Paths ---
    PROJECT_ROOT: Path = field(default_factory=lambda: _PROJECT_ROOT)
    DATA_RAW_DIR: Path = field(default_factory=lambda: _PROJECT_ROOT / "data" / "raw")
    DATA_PROCESSED_DIR: Path = field(default_factory=lambda: _PROJECT_ROOT / "data" / "processed")

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


# Instancia singleton — importar esta variable directamente
settings = Settings()
