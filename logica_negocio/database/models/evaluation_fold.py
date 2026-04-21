"""
DEMAND-24 — SQLAlchemy Model: EvaluationFold

Almacena métricas de evaluación por fold de cross-validation.
Permite auditar el rendimiento del modelo en cada iteración de WalkForward.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric

from .base import Base


def _utcnow() -> datetime:
    """Genera timestamp UTC actual."""
    return datetime.now(timezone.utc)


class EvaluationFold(Base):
    """
    Modelo ORM para la tabla 'evaluation_fold'.

    Campos:
        id: Identificador autoincremental.
        fold_number: Número del fold en TimeSeriesSplit (1-indexed).
        sku_id: FK → sku(id) (opcional, puede ser evaluación global).
        mape: Mean Absolute Percentage Error del fold.
        mae: Mean Absolute Error del fold.
        bias: Sesgo medio del fold.
        created_at: Timestamp de creación.
    """

    __tablename__ = "evaluation_fold"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fold_number = Column(Integer, nullable=False)
    sku_id = Column(
        Integer,
        ForeignKey("sku.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    mape = Column(Numeric(5, 2), nullable=True)
    mae = Column(Numeric(10, 2), nullable=True)
    bias = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<EvaluationFold(id={self.id}, fold={self.fold_number}, "
            f"sku_id={self.sku_id}, mape={self.mape})>"
        )
