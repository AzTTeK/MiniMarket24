"""
DEMAND-24 — SQLAlchemy Model: ModelVersion

Metadata de cada versión de modelo entrenado.
Permite auditar qué hiperparámetros se usaron, cuándo se entrenó,
y si cumplió el criterio de aceptación CA-01.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from .base import Base


def _utcnow() -> datetime:
    """Genera timestamp UTC actual."""
    return datetime.now(timezone.utc)


class ModelVersion(Base):
    """
    Modelo ORM para la tabla 'model_version'.

    Campos:
        id: Identificador autoincremental.
        version: Versión semántica del modelo (e.g., 'v1.0.0'). UNIQUE.
        training_date: Fecha/hora del entrenamiento.
        random_seed: Semilla usada para reproducibilidad (Regla VI).
        n_splits: Número de folds en TimeSeriesSplit.
        xgboost_params: Hiperparámetros como JSONB (PostgreSQL) o JSON (SQLite).
        acceptance_criteria_met: ¿Cumplió CA-01 (70% SKU ≤ 20% MAPE)?
        created_at: Timestamp de creación.

    Nota sobre xgboost_params:
        Usamos JSON genérico como tipo base con .with_variant(JSONB, 'postgresql')
        para compatibilidad con SQLite en tests y PostgreSQL en producción.
    """

    __tablename__ = "model_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), unique=True, nullable=False, index=True)
    training_date = Column(DateTime(timezone=True), default=_utcnow)
    random_seed = Column(Integer, nullable=True)
    n_splits = Column(Integer, nullable=True)
    xgboost_params = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    acceptance_criteria_met = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<ModelVersion(id={self.id}, version='{self.version}', "
            f"ca01_met={self.acceptance_criteria_met})>"
        )
