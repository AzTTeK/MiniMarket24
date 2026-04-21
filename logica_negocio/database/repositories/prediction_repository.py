"""
DEMAND-24 — Repository: PredictionRepository

Maneja operaciones CRUD sobre la tabla 'prediction'.
Incluye bulk_create para insertar múltiples predicciones de una vez.
"""

import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logica_negocio.database.models.prediction import Prediction
from logica_negocio.database.schemas.prediction import (
    PredictionCreate,
    PredictionRead,
    PredictionUpdate,
)

logger = logging.getLogger(__name__)


class PredictionRepository:
    """
    Repository para operaciones CRUD sobre predicciones.

    Métodos de negocio adicionales:
    - get_by_sku_week: busca por combinación única (sku_id, week_start)
    - get_all_by_sku: obtiene todas las predicciones de un SKU
    - bulk_create: inserción masiva para batch de predicciones
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, prediction_data: PredictionCreate) -> PredictionRead:
        """
        Crea una nueva predicción.

        Raises:
            ValueError: Si ya existe predicción para ese SKU + semana.
        """
        logger.info(
            "Creando predicción: sku_id=%d, week_start=%s",
            prediction_data.sku_id,
            prediction_data.week_start,
        )

        db_prediction = Prediction(**prediction_data.model_dump())

        try:
            self.db.add(db_prediction)
            self.db.commit()
            self.db.refresh(db_prediction)
        except IntegrityError:
            self.db.rollback()
            logger.error(
                "Predicción duplicada: sku_id=%d, week_start=%s",
                prediction_data.sku_id,
                prediction_data.week_start,
            )
            raise ValueError(
                f"Ya existe predicción para sku_id={prediction_data.sku_id}, "
                f"week_start={prediction_data.week_start}"
            )

        return PredictionRead.model_validate(db_prediction)

    def get_by_id(self, prediction_id: int) -> Optional[PredictionRead]:
        """Obtener una predicción por su ID."""
        result = self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if result is None:
            return None
        return PredictionRead.model_validate(result)

    def get_by_sku_week(self, sku_id: int, week_start: date) -> Optional[PredictionRead]:
        """Obtener la predicción para un SKU + semana específica."""
        result = (
            self.db.query(Prediction)
            .filter(Prediction.sku_id == sku_id, Prediction.week_start == week_start)
            .first()
        )
        if result is None:
            return None
        return PredictionRead.model_validate(result)

    def get_all_by_sku(self, sku_id: int) -> List[PredictionRead]:
        """Obtener todas las predicciones de un SKU, ordenadas por semana."""
        results = (
            self.db.query(Prediction)
            .filter(Prediction.sku_id == sku_id)
            .order_by(Prediction.week_start)
            .all()
        )
        return [PredictionRead.model_validate(r) for r in results]

    def get_all(self) -> List[PredictionRead]:
        """Obtener todas las predicciones."""
        results = self.db.query(Prediction).order_by(Prediction.created_at).all()
        return [PredictionRead.model_validate(r) for r in results]

    def bulk_create(self, predictions: List[PredictionCreate]) -> List[PredictionRead]:
        """
        Inserta múltiples predicciones en una sola transacción.

        Args:
            predictions: Lista de DTOs PredictionCreate.

        Returns:
            Lista de PredictionRead con IDs asignados.

        Raises:
            ValueError: Si alguna predicción viola constraint UNIQUE.
        """
        logger.info("Bulk insert: %d predicciones", len(predictions))

        db_predictions = [Prediction(**p.model_dump()) for p in predictions]

        try:
            self.db.add_all(db_predictions)
            self.db.commit()
            for db_pred in db_predictions:
                self.db.refresh(db_pred)
        except IntegrityError:
            self.db.rollback()
            logger.error("Error de integridad en bulk insert")
            raise ValueError("Predicción duplicada en bulk insert")

        logger.info("Bulk insert completado: %d predicciones", len(db_predictions))
        return [PredictionRead.model_validate(p) for p in db_predictions]

    def update(self, prediction_id: int, prediction_data: PredictionUpdate) -> Optional[PredictionRead]:
        """Actualizar una predicción existente."""
        db_prediction = self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if db_prediction is None:
            return None

        update_data = prediction_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            if value is not None:
                setattr(db_prediction, field_name, value)

        self.db.commit()
        self.db.refresh(db_prediction)
        return PredictionRead.model_validate(db_prediction)

    def delete(self, prediction_id: int) -> bool:
        """Eliminar una predicción por su ID."""
        db_prediction = self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if db_prediction is None:
            return False

        self.db.delete(db_prediction)
        self.db.commit()
        logger.info("Predicción eliminada: id=%d", prediction_id)
        return True
