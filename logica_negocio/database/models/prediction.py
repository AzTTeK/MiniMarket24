"""
DEMAND-24 — SQLAlchemy Model: Prediction

Almacena predicciones de demanda generadas por el Módulo Analítico.
Mapea directamente a la tabla 'prediction' en Supabase.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)

from .base import Base


def _utcnow() -> datetime:
    """Genera timestamp UTC actual."""
    return datetime.now(timezone.utc)


class Prediction(Base):
    """
    Modelo ORM para la tabla 'prediction'.

    Campos:
        id: Identificador autoincremental.
        sku_id: FK → sku(id).
        week_start: Inicio de la semana predicha (DATE).
        predicted_demand: Demanda estimada.
        confidence_level: Nivel de confianza (0.00 a 1.00).
        lower_bound: Límite inferior del intervalo de confianza.
        upper_bound: Límite superior del intervalo de confianza.
        mape: Error porcentual absoluto medio del SKU.
        created_at: Timestamp de creación.

    Constraints:
        UNIQUE(sku_id, week_start) — solo una predicción por SKU-semana.
    """

    __tablename__ = "prediction"
    __table_args__ = (
        UniqueConstraint("sku_id", "week_start", name="uq_prediction_sku_week"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(
        Integer,
        ForeignKey("sku.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_start = Column(Date, nullable=False, index=True)
    predicted_demand = Column(Numeric(10, 2), nullable=False)
    confidence_level = Column(Numeric(3, 2), nullable=True)
    lower_bound = Column(Numeric(10, 2), nullable=True)
    upper_bound = Column(Numeric(10, 2), nullable=True)
    mape = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<Prediction(id={self.id}, sku_id={self.sku_id}, "
            f"week_start={self.week_start}, demand={self.predicted_demand})>"
        )
