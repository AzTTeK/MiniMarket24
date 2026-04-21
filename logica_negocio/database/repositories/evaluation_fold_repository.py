"""
DEMAND-24 — Repository: EvaluationFoldRepository

Maneja operaciones CRUD sobre la tabla 'evaluation_fold'.
Almacena métricas por fold de walk-forward cross-validation.
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from logica_negocio.database.models.evaluation_fold import EvaluationFold
from logica_negocio.database.schemas.evaluation_fold import (
    EvaluationFoldCreate,
    EvaluationFoldRead,
    EvaluationFoldUpdate,
)

logger = logging.getLogger(__name__)


class EvaluationFoldRepository:
    """
    Repository para operaciones CRUD sobre registros de evaluación por fold.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, fold_data: EvaluationFoldCreate) -> EvaluationFoldRead:
        """Crea un nuevo registro de evaluación por fold."""
        logger.info(
            "Creando evaluación: fold=%d, sku_id=%s",
            fold_data.fold_number,
            fold_data.sku_id,
        )

        db_fold = EvaluationFold(**fold_data.model_dump())
        self.db.add(db_fold)
        self.db.commit()
        self.db.refresh(db_fold)

        return EvaluationFoldRead.model_validate(db_fold)

    def get_by_id(self, fold_id: int) -> Optional[EvaluationFoldRead]:
        """Obtener un registro de evaluación por su ID."""
        result = self.db.query(EvaluationFold).filter(EvaluationFold.id == fold_id).first()
        if result is None:
            return None
        return EvaluationFoldRead.model_validate(result)

    def get_by_fold(self, fold_number: int) -> List[EvaluationFoldRead]:
        """Obtener todos los registros de un fold específico."""
        results = (
            self.db.query(EvaluationFold)
            .filter(EvaluationFold.fold_number == fold_number)
            .all()
        )
        return [EvaluationFoldRead.model_validate(r) for r in results]

    def get_all_by_sku(self, sku_id: int) -> List[EvaluationFoldRead]:
        """Obtener todas las evaluaciones de un SKU, ordenadas por fold."""
        results = (
            self.db.query(EvaluationFold)
            .filter(EvaluationFold.sku_id == sku_id)
            .order_by(EvaluationFold.fold_number)
            .all()
        )
        return [EvaluationFoldRead.model_validate(r) for r in results]

    def get_all(self) -> List[EvaluationFoldRead]:
        """Obtener todos los registros de evaluación."""
        results = self.db.query(EvaluationFold).order_by(EvaluationFold.fold_number).all()
        return [EvaluationFoldRead.model_validate(r) for r in results]

    def update(self, fold_id: int, fold_data: EvaluationFoldUpdate) -> Optional[EvaluationFoldRead]:
        """Actualizar métricas de un fold existente."""
        db_fold = self.db.query(EvaluationFold).filter(EvaluationFold.id == fold_id).first()
        if db_fold is None:
            return None

        update_data = fold_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            if value is not None:
                setattr(db_fold, field_name, value)

        self.db.commit()
        self.db.refresh(db_fold)
        return EvaluationFoldRead.model_validate(db_fold)

    def delete(self, fold_id: int) -> bool:
        """Eliminar un registro de evaluación por su ID."""
        db_fold = self.db.query(EvaluationFold).filter(EvaluationFold.id == fold_id).first()
        if db_fold is None:
            return False

        self.db.delete(db_fold)
        self.db.commit()
        logger.info("Evaluación eliminada: id=%d", fold_id)
        return True

    def bulk_create(self, folds: List[EvaluationFoldCreate]) -> List[EvaluationFoldRead]:
        """Inserta múltiples registros de evaluación en una transacción."""
        logger.info("Bulk insert: %d evaluaciones", len(folds))

        db_folds = [EvaluationFold(**f.model_dump()) for f in folds]
        self.db.add_all(db_folds)
        self.db.commit()
        for db_fold in db_folds:
            self.db.refresh(db_fold)

        return [EvaluationFoldRead.model_validate(f) for f in db_folds]
