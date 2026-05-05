"""
DEMAND-24 — Repository: AlertRepository

Maneja operaciones CRUD sobre la tabla 'alert'.
Incluye consultas especializadas: alertas activas, por SKU, acknowledge.
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from logica_negocio.database.models.alert import Alert
from logica_negocio.database.schemas.alert import (
    AlertCreate,
    AlertRead,
    AlertUpdate,
)

logger = logging.getLogger(__name__)


class AlertRepository:
    """
    Repository para operaciones CRUD sobre alertas.

    Métodos de negocio:
    - get_active: alertas no atendidas
    - get_by_sku: alertas de un SKU específico
    - acknowledge: marcar alerta como atendida
    - bulk_create: inserción masiva de alertas
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, alert_data: AlertCreate) -> AlertRead:
        """Crea una nueva alerta."""
        logger.info(
            "Creando alerta: sku_id=%d, type=%s",
            alert_data.sku_id,
            alert_data.alert_type,
        )

        db_alert = Alert(**alert_data.model_dump())
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)

        return AlertRead.model_validate(db_alert)

    def get_by_id(self, alert_id: int) -> Optional[AlertRead]:
        """Obtener una alerta por su ID."""
        result = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if result is None:
            return None
        return AlertRead.model_validate(result)

    def get_active(self) -> List[AlertRead]:
        """Obtener todas las alertas activas (no atendidas)."""
        results = (
            self.db.query(Alert)
            .filter(Alert.is_acknowledged == False)  # noqa: E712
            .order_by(Alert.created_at.desc())
            .all()
        )
        return [AlertRead.model_validate(r) for r in results]

    def get_by_sku(self, sku_id: int) -> List[AlertRead]:
        """Obtener todas las alertas de un SKU, más recientes primero."""
        results = (
            self.db.query(Alert)
            .filter(Alert.sku_id == sku_id)
            .order_by(Alert.created_at.desc())
            .all()
        )
        return [AlertRead.model_validate(r) for r in results]

    def get_all(self) -> List[AlertRead]:
        """Obtener todas las alertas."""
        results = self.db.query(Alert).order_by(Alert.created_at.desc()).all()
        return [AlertRead.model_validate(r) for r in results]

    def acknowledge(self, alert_id: int) -> Optional[AlertRead]:
        """Marca una alerta como atendida."""
        db_alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if db_alert is None:
            return None

        db_alert.is_acknowledged = True
        self.db.commit()
        self.db.refresh(db_alert)

        logger.info("Alerta atendida: id=%d", alert_id)
        return AlertRead.model_validate(db_alert)

    def bulk_create(self, alerts: List[AlertCreate]) -> List[AlertRead]:
        """Inserta múltiples alertas en una transacción."""
        logger.info("Bulk insert: %d alertas", len(alerts))

        db_alerts = [Alert(**a.model_dump()) for a in alerts]
        self.db.add_all(db_alerts)
        self.db.commit()
        for db_alert in db_alerts:
            self.db.refresh(db_alert)

        return [AlertRead.model_validate(a) for a in db_alerts]

    def delete(self, alert_id: int) -> bool:
        """Eliminar una alerta por su ID."""
        db_alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if db_alert is None:
            return False

        self.db.delete(db_alert)
        self.db.commit()
        logger.info("Alerta eliminada: id=%d", alert_id)
        return True
