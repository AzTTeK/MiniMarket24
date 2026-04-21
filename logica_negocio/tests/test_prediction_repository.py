"""
DEMAND-24 — Tests: PredictionRepository

Tests CRUD + bulk_create + get_by_sku_week + manejo de duplicados.
"""

from datetime import date

import pytest

from logica_negocio.database.models.sku import Sku
from logica_negocio.database.repositories.prediction_repository import PredictionRepository
from logica_negocio.database.schemas.prediction import PredictionCreate, PredictionUpdate


def _create_test_sku(db_session, sku_code: str = "TEST_SKU") -> int:
    """Helper: Crea un SKU en la BD y retorna su ID."""
    sku = Sku(sku_code=sku_code, description="Test SKU")
    db_session.add(sku)
    db_session.commit()
    db_session.refresh(sku)
    return sku.id


class TestPredictionRepository:
    """Tests para PredictionRepository."""

    def test_create_prediction_success(self, test_db):
        """Crear una predicción deve retornar PredictionRead con ID."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)

        pred = repo.create(PredictionCreate(
            sku_id=sku_id,
            week_start=date(2026, 1, 5),
            predicted_demand=150.0,
            confidence_level=0.90,
            lower_bound=140.0,
            upper_bound=160.0,
            mape=5.0,
        ))

        assert pred.id is not None
        assert pred.sku_id == sku_id
        assert pred.predicted_demand == 150.0

    def test_create_prediction_duplicate_raises(self, test_db):
        """Predicción duplicada (mismo sku_id + week_start) debe lanzar ValueError."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)

        repo.create(PredictionCreate(
            sku_id=sku_id,
            week_start=date(2026, 1, 5),
            predicted_demand=100.0,
        ))
        with pytest.raises(ValueError, match="Ya existe"):
            repo.create(PredictionCreate(
                sku_id=sku_id,
                week_start=date(2026, 1, 5),
                predicted_demand=200.0,
            ))

    def test_get_by_id_existing(self, test_db):
        """Obtener predicción por ID existente."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)
        created = repo.create(PredictionCreate(
            sku_id=sku_id,
            week_start=date(2026, 2, 2),
            predicted_demand=80.0,
        ))

        found = repo.get_by_id(created.id)
        assert found is not None
        assert found.predicted_demand == 80.0

    def test_get_by_sku_week(self, test_db):
        """Buscar por combinación única sku_id + week_start."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)

        repo.create(PredictionCreate(
            sku_id=sku_id,
            week_start=date(2026, 3, 2),
            predicted_demand=120.0,
        ))

        found = repo.get_by_sku_week(sku_id, date(2026, 3, 2))
        assert found is not None
        assert found.predicted_demand == 120.0

    def test_get_by_sku_week_nonexistent(self, test_db):
        """Buscar sku_id + week_start inexistente retorna None."""
        repo = PredictionRepository(test_db)
        assert repo.get_by_sku_week(999, date(2026, 1, 1)) is None

    def test_get_all_by_sku(self, test_db):
        """Obtener todas las predicciones de un SKU."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)

        repo.create(PredictionCreate(
            sku_id=sku_id, week_start=date(2026, 1, 5), predicted_demand=100.0))
        repo.create(PredictionCreate(
            sku_id=sku_id, week_start=date(2026, 1, 12), predicted_demand=110.0))

        results = repo.get_all_by_sku(sku_id)
        assert len(results) == 2
        assert results[0].week_start == date(2026, 1, 5)  # Ordenado por week_start

    def test_bulk_create(self, test_db):
        """bulk_create deve insertar múltiples predicciones."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)

        predictions = [
            PredictionCreate(
                sku_id=sku_id,
                week_start=date(2026, 4, week * 7),
                predicted_demand=100.0 + week,
            )
            for week in range(1, 4)  # 3 predicciones
        ]

        results = repo.bulk_create(predictions)
        assert len(results) == 3

    def test_update_prediction(self, test_db):
        """Actualizar predicción existente."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)
        created = repo.create(PredictionCreate(
            sku_id=sku_id, week_start=date(2026, 5, 4), predicted_demand=100.0))

        updated = repo.update(created.id, PredictionUpdate(predicted_demand=200.0))
        assert updated is not None
        assert updated.predicted_demand == 200.0

    def test_delete_prediction(self, test_db):
        """Eliminar predicción existente."""
        sku_id = _create_test_sku(test_db)
        repo = PredictionRepository(test_db)
        created = repo.create(PredictionCreate(
            sku_id=sku_id, week_start=date(2026, 6, 1), predicted_demand=50.0))

        assert repo.delete(created.id) is True
        assert repo.get_by_id(created.id) is None

    def test_delete_nonexistent(self, test_db):
        """Eliminar predicción inexistente retorna False."""
        repo = PredictionRepository(test_db)
        assert repo.delete(999) is False
