"""
DEMAND-24 — Tests: EvaluationFoldRepository

Tests CRUD + get_by_fold + get_all_by_sku + bulk_create.
"""

import pytest

from logica_negocio.database.models.sku import Sku
from logica_negocio.database.repositories.evaluation_fold_repository import (
    EvaluationFoldRepository,
)
from logica_negocio.database.schemas.evaluation_fold import (
    EvaluationFoldCreate,
    EvaluationFoldUpdate,
)


def _create_test_sku(db_session, sku_code: str = "EVAL_SKU") -> int:
    """Helper: Crea un SKU para tests."""
    sku = Sku(sku_code=sku_code)
    db_session.add(sku)
    db_session.commit()
    db_session.refresh(sku)
    return sku.id


class TestEvaluationFoldRepository:
    """Tests para EvaluationFoldRepository."""

    def test_create_evaluation_fold(self, test_db):
        """Crear un registro de evaluación por fold."""
        sku_id = _create_test_sku(test_db)
        repo = EvaluationFoldRepository(test_db)

        fold = repo.create(EvaluationFoldCreate(
            fold_number=1,
            sku_id=sku_id,
            mape=12.5,
            mae=45.0,
            bias=-2.3,
        ))

        assert fold.id is not None
        assert fold.fold_number == 1
        assert fold.mape == 12.5

    def test_create_fold_without_sku(self, test_db):
        """Crear evaluación global (sin sku_id específico)."""
        repo = EvaluationFoldRepository(test_db)

        fold = repo.create(EvaluationFoldCreate(
            fold_number=1,
            mape=15.0,
            mae=50.0,
            bias=0.0,
        ))

        assert fold.id is not None
        assert fold.sku_id is None

    def test_get_by_id(self, test_db):
        """Obtener evaluación por ID."""
        repo = EvaluationFoldRepository(test_db)
        created = repo.create(EvaluationFoldCreate(fold_number=2, mape=10.0))

        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.fold_number == 2

    def test_get_by_fold(self, test_db):
        """Obtener registros por número de fold."""
        repo = EvaluationFoldRepository(test_db)
        sku_id = _create_test_sku(test_db)

        repo.create(EvaluationFoldCreate(fold_number=3, sku_id=sku_id, mape=8.0))
        repo.create(EvaluationFoldCreate(fold_number=3, mape=9.0))  # Global

        results = repo.get_by_fold(3)
        assert len(results) == 2

    def test_get_all_by_sku(self, test_db):
        """Obtener evaluaciones de un SKU ordenadas por fold."""
        sku_id = _create_test_sku(test_db)
        repo = EvaluationFoldRepository(test_db)

        repo.create(EvaluationFoldCreate(fold_number=2, sku_id=sku_id, mape=12.0))
        repo.create(EvaluationFoldCreate(fold_number=1, sku_id=sku_id, mape=14.0))

        results = repo.get_all_by_sku(sku_id)
        assert len(results) == 2
        assert results[0].fold_number == 1
        assert results[1].fold_number == 2

    def test_update_evaluation(self, test_db):
        """Actualizar métricas de un fold."""
        repo = EvaluationFoldRepository(test_db)
        created = repo.create(EvaluationFoldCreate(fold_number=1, mape=20.0))

        updated = repo.update(created.id, EvaluationFoldUpdate(mape=15.0))
        assert updated is not None
        assert updated.mape == 15.0

    def test_delete_evaluation(self, test_db):
        """Eliminar registro de evaluación."""
        repo = EvaluationFoldRepository(test_db)
        created = repo.create(EvaluationFoldCreate(fold_number=1, mape=10.0))

        assert repo.delete(created.id) is True
        assert repo.get_by_id(created.id) is None

    def test_bulk_create(self, test_db):
        """Insertar múltiples evaluaciones de una vez."""
        sku_id = _create_test_sku(test_db)
        repo = EvaluationFoldRepository(test_db)

        folds = [
            EvaluationFoldCreate(fold_number=i, sku_id=sku_id, mape=10.0 + i)
            for i in range(1, 6)  # 5 folds
        ]

        results = repo.bulk_create(folds)
        assert len(results) == 5
