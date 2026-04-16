"""
DEMAND-24 — Configuración del Módulo Analítico

Punto único de acceso a todos los hiperparámetros y constantes de ML.
Los valores se cargan desde .env vía settings.py para cumplir con la
Regla VIII (Zero Tolerance a valores hardcodeados).
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from logica_negocio.config.settings import settings


def _get_ml_env_int(key: str, default: int) -> int:
    """Obtiene una variable de entorno ML como entero."""
    import os
    raw = os.getenv(key, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _get_ml_env_float(key: str, default: float) -> float:
    """Obtiene una variable de entorno ML como flotante."""
    import os
    raw = os.getenv(key, str(default))
    try:
        return float(raw)
    except ValueError:
        return default


def _get_ml_env_bool(key: str, default: bool = False) -> bool:
    """Obtiene una variable de entorno ML como booleano."""
    import os
    raw = os.getenv(key, str(default)).lower()
    return raw in ("true", "1", "yes", "si")


@dataclass(frozen=True)
class MLConfig:
    """Configuración inmutable del Módulo Analítico."""

    # --- Reproducibilidad (Regla VI) ---
    RANDOM_SEED: int = field(
        default_factory=lambda: _get_ml_env_int("ML_RANDOM_SEED", 42)
    )

    # --- Validación Temporal (Regla VI - Anti-Leakage) ---
    N_SPLITS: int = field(
        default_factory=lambda: _get_ml_env_int("ML_N_SPLITS", 5)
    )
    MIN_WEEKS_HISTORY: int = field(
        default_factory=lambda: settings.MIN_WEEKS_HISTORY
    )

    # --- Intervalos de Confianza (RF-03) ---
    CONFIDENCE_LEVEL: float = field(
        default_factory=lambda: _get_ml_env_float("ML_CONFIDENCE_LEVEL", 0.90)
    )
    LOWER_QUANTILE: float = field(
        default_factory=lambda: (1.0 - _get_ml_env_float("ML_CONFIDENCE_LEVEL", 0.90)) / 2
    )
    UPPER_QUANTILE: float = field(
        default_factory=lambda: 1.0 - (1.0 - _get_ml_env_float("ML_CONFIDENCE_LEVEL", 0.90)) / 2
    )

    # --- Thresholds de Negocio (RNF-07) ---
    MAPE_LOW_CONFIDENCE_THRESHOLD: float = field(
        default_factory=lambda: settings.MAPE_LOW_CONFIDENCE_THRESHOLD
    )

    # --- SKU Piloto (RF-01) ---
    PILOT_SKU_IDS: list[str] = field(
        default_factory=lambda: settings.PILOT_SKU_IDS
    )

    # --- Hiperparámetros XGBoost ---
    XGBOOST_MAX_DEPTH: int = field(
        default_factory=lambda: _get_ml_env_int("ML_XGBOOST_MAX_DEPTH", 6)
    )
    XGBOOST_LEARNING_RATE: float = field(
        default_factory=lambda: _get_ml_env_float("ML_XGBOOST_LEARNING_RATE", 0.1)
    )
    XGBOOST_N_ESTIMATORS: int = field(
        default_factory=lambda: _get_ml_env_int("ML_XGBOOST_N_ESTIMATORS", 100)
    )
    XGBOOST_SUBSAMPLE: float = field(
        default_factory=lambda: _get_ml_env_float("ML_XGBOOST_SUBSAMPLE", 0.8)
    )
    XGBOOST_COLSAMPLE_BYTREE: float = field(
        default_factory=lambda: _get_ml_env_float("ML_XGBOOST_COLSAMPLE_BYTREE", 0.8)
    )

    # --- Paths ---
    PROJECT_ROOT: Path = field(default_factory=lambda: settings.PROJECT_ROOT)
    DATA_RAW_DIR: Path = field(default_factory=lambda: settings.DATA_RAW_DIR)
    DATA_PROCESSED_DIR: Path = field(default_factory=lambda: settings.DATA_PROCESSED_DIR)
    ML_MODELS_DIR: Path = field(
        default_factory=lambda: settings.PROJECT_ROOT / "modulo_analitico" / "models" / "saved"
    )

    # --- Selección de familias piloto (subconjunto estratégico) ---
    PILOT_FAMILIES: list[str] = field(
        default_factory=lambda: [
            "BEVERAGES",
            "DAIRY",
            "GROCERY I",
            "PRODUCE",
            "MEATS",
            "BREAD/BAKERY",
            "CLEANING",
            "HOME CARE",
            "PERSONAL CARE",
            "EGGS",
        ]
    )

    # --- Validaciones ---
    def validate(self) -> None:
        """Valida que la configuración sea consistente."""
        if not (0 < self.CONFIDENCE_LEVEL < 1):
            raise ValueError(f"CONFIDENCE_LEVEL debe estar entre 0 y 1: {self.CONFIDENCE_LEVEL}")
        if self.MIN_WEEKS_HISTORY < 1:
            raise ValueError(f"MIN_WEEKS_HISTORY debe ser >= 1: {self.MIN_WEEKS_HISTORY}")
        if self.N_SPLITS < 2:
            raise ValueError(f"N_SPLITS debe ser >= 2: {self.N_SPLITS}")
        if self.XGBOOST_MAX_DEPTH < 1:
            raise ValueError(f"XGBOOST_MAX_DEPTH debe ser >= 1: {self.XGBOOST_MAX_DEPTH}")
        if not (0 < self.XGBOOST_LEARNING_RATE <= 1):
            raise ValueError(f"XGBOOST_LEARNING_RATE debe estar entre 0 y 1: {self.XGBOOST_LEARNING_RATE}")
        if self.XGBOOST_N_ESTIMATORS < 1:
            raise ValueError(f"XGBOOST_N_ESTIMATORS debe ser >= 1: {self.XGBOOST_N_ESTIMATORS}")
        if not (0 < self.XGBOOST_SUBSAMPLE <= 1):
            raise ValueError(f"XGBOOST_SUBSAMPLE debe estar entre 0 y 1: {self.XGBOOST_SUBSAMPLE}")
        if not (0 < self.XGBOOST_COLSAMPLE_BYTREE <= 1):
            raise ValueError(f"XGBOOST_COLSAMPLE_BYTREE debe estar entre 0 y 1: {self.XGBOOST_COLSAMPLE_BYTREE}")

    @property
    def xgboost_params(self) -> dict:
        """Retorna los hiperparámetros de XGBoost como diccionario."""
        return {
            "max_depth": self.XGBOOST_MAX_DEPTH,
            "learning_rate": self.XGBOOST_LEARNING_RATE,
            "n_estimators": self.XGBOOST_N_ESTIMATORS,
            "subsample": self.XGBOOST_SUBSAMPLE,
            "colsample_bytree": self.XGBOOST_COLSAMPLE_BYTREE,
            "random_state": self.RANDOM_SEED,
        }


ml_config = MLConfig()
ml_config.validate()
