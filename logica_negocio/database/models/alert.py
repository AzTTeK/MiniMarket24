"""
DEMAND-24 — ORM Model: Alert

Almacena alertas de quiebre de stock generadas por el Motor de Alertas.
Implementa RF-04 (Alertas de Quiebre de Stock) del SRS.

Formato de mensaje SRS:
    "Posible quiebre de stock: [SKU] — Demanda proyectada: X uds, Stock actual: Y uds."
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from .base import Base


def _utcnow() -> datetime:
    """Genera timestamp UTC actual."""
    return datetime.now(timezone.utc)


class Alert(Base):
    """
    Modelo ORM para la tabla 'alert'.

    Campos:
        id: Identificador autoincremental.
        sku_id: FK → sku(id).
        prediction_id: FK → prediction(id) (nullable, puede ser alerta manual).
        alert_type: Tipo de alerta ('stock_break', 'low_confidence', 'data_quality').
        message: Mensaje descriptivo de la alerta (formato SRS RF-04).
        is_acknowledged: Si el administrador ya atendió la alerta.
        created_at: Timestamp de creación.
    """

    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(
        Integer,
        ForeignKey("sku.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction_id = Column(
        Integer,
        ForeignKey("prediction.id", ondelete="SET NULL"),
        nullable=True,
    )
    alert_type = Column(String(30), nullable=False, index=True)
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:
        return (
            f"<Alert(id={self.id}, sku_id={self.sku_id}, "
            f"type='{self.alert_type}', ack={self.is_acknowledged})>"
        )
