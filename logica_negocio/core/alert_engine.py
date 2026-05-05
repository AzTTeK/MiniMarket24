"""
DEMAND-24 — Motor de Alertas (Alert Engine)

Implementa RF-04 del SRS: Alertas de Quiebre de Stock.

Lógica:
    Si demanda_proyectada > stock_actual para un SKU →
    genera alerta con formato:
        "Posible quiebre de stock: [SKU] — Demanda proyectada: X uds, Stock actual: Y uds."

Cumple con:
- Regla I: Solo lógica de alertas, no toca ML ni UI
- Regla IV: Función hace una sola cosa (generar alertas)
"""

import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from logica_negocio.database.repositories.alert_repository import AlertRepository
from logica_negocio.database.repositories.prediction_repository import PredictionRepository
from logica_negocio.database.schemas.alert import AlertCreate, AlertRead

logger = logging.getLogger(__name__)

# Constantes de tipos de alerta
ALERT_TYPE_STOCK_BREAK = "stock_break"
ALERT_TYPE_LOW_CONFIDENCE = "low_confidence"


class AlertEngine:
    """
    Motor de alertas para detección de quiebre de stock.

    Compara predicciones de demanda contra niveles de stock actual
    y genera alertas cuando hay riesgo de desabastecimiento.

    Usage:
        engine = AlertEngine(db_session)
        alerts = engine.check_stock_alerts(stock_levels)
    """

    def __init__(self, db: Session):
        self._db = db
        self._alert_repo = AlertRepository(db)
        self._prediction_repo = PredictionRepository(db)

    def check_stock_alerts(
        self,
        stock_levels: Dict[int, int],
    ) -> List[AlertRead]:
        """
        Compara predicciones recientes contra stock actual y genera alertas.

        Args:
            stock_levels: Diccionario {sku_id: stock_actual} con niveles
                         de inventario actuales por SKU.

        Returns:
            Lista de alertas generadas (AlertRead).

        Notes:
            Solo evalúa SKUs que tienen tanto predicciones como stock registrado.
            Formato de alerta según RF-04 del SRS.
        """
        if not stock_levels:
            logger.info("Sin niveles de stock para evaluar")
            return []

        alerts_to_create: List[AlertCreate] = []

        for sku_id, stock_actual in stock_levels.items():
            predictions = self._prediction_repo.get_all_by_sku(sku_id)
            if not predictions:
                continue

            latest_prediction = predictions[-1]
            predicted_demand = float(latest_prediction.predicted_demand)

            if predicted_demand <= stock_actual:
                continue

            message = (
                f"Posible quiebre de stock: SKU #{sku_id} — "
                f"Demanda proyectada: {predicted_demand:.0f} uds, "
                f"Stock actual: {stock_actual} uds."
            )

            alert = AlertCreate(
                sku_id=sku_id,
                prediction_id=latest_prediction.id,
                alert_type=ALERT_TYPE_STOCK_BREAK,
                message=message,
            )
            alerts_to_create.append(alert)

            logger.info(
                "Alerta detectada: sku_id=%d, demand=%.0f, stock=%d",
                sku_id, predicted_demand, stock_actual,
            )

        if not alerts_to_create:
            logger.info("Sin alertas de quiebre de stock detectadas")
            return []

        created_alerts = self._alert_repo.bulk_create(alerts_to_create)
        logger.info("Generadas %d alertas de quiebre de stock", len(created_alerts))
        return created_alerts

    def check_low_confidence_alerts(
        self,
        mape_threshold: float = 25.0,
    ) -> List[AlertRead]:
        """
        Genera alertas para predicciones de baja confianza (RNF-07).

        Args:
            mape_threshold: Umbral MAPE (default 25.0 desde .env).

        Returns:
            Lista de alertas generadas.
        """
        all_predictions = self._prediction_repo.get_all()
        alerts_to_create: List[AlertCreate] = []

        for prediction in all_predictions:
            if prediction.mape is None:
                continue

            if float(prediction.mape) <= mape_threshold:
                continue

            message = (
                f"Predicción de baja confianza: SKU #{prediction.sku_id} — "
                f"MAPE: {float(prediction.mape):.1f}% (umbral: {mape_threshold}%)"
            )

            alert = AlertCreate(
                sku_id=prediction.sku_id,
                prediction_id=prediction.id,
                alert_type=ALERT_TYPE_LOW_CONFIDENCE,
                message=message,
            )
            alerts_to_create.append(alert)

        if not alerts_to_create:
            return []

        created_alerts = self._alert_repo.bulk_create(alerts_to_create)
        logger.info("Generadas %d alertas de baja confianza", len(created_alerts))
        return created_alerts

    def get_active_alerts(self) -> List[AlertRead]:
        """Obtiene todas las alertas activas (no atendidas)."""
        return self._alert_repo.get_active()

    def acknowledge_alert(self, alert_id: int) -> AlertRead | None:
        """Marca una alerta como atendida."""
        return self._alert_repo.acknowledge(alert_id)
