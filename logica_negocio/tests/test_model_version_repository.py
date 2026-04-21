"""
DEMAND-24 — Tests: ModelVersionRepository

Tests CRUD + get_by_version + get_latest + duplicados.
"""

from datetime import datetime, timezone

import pytest

from logica_negocio.database.repositories.model_version_repository import (
    ModelVersionRepository,
)
from logica_negocio.database.schemas.model_version import (
    ModelVersionCreate,
    ModelVersionUpdate,
)


class TestModelVersionRepository:
    """Tests para ModelVersionRepository."""

    def test_create_model_version(self, test_db):
        """Registrar una nueva versión de modelo."""
        repo = ModelVersionRepository(test_db)

        version = repo.create(ModelVersionCreate(
            version="v1.0.0",
            random_seed=42,
            n_splits=5,
            xgboost_params={"max_depth": 6, "learning_rate": 0.1},
            acceptance_criteria_met=True,
        ))

        assert version.id is not None
        assert version.version == "v1.0.0"
        assert version.random_seed == 42
        assert version.acceptance_criteria_met is True

    def test_create_duplicate_version_raises(self, test_db):
        """Versión duplicada debe lanzar ValueError."""
        repo = ModelVersionRepository(test_db)
        repo.create(ModelVersionCreate(version="v1.0.0"))

        with pytest.raises(ValueError, match="ya existe"):
            repo.create(ModelVersionCreate(version="v1.0.0"))

    def test_get_by_version(self, test_db):
        """Buscar por string de versión."""
        repo = ModelVersionRepository(test_db)
        repo.create(ModelVersionCreate(version="v2.0.0", n_splits=3))

        found = repo.get_by_version("v2.0.0")
        assert found is not None
        assert found.n_splits == 3

    def test_get_by_version_nonexistent(self, test_db):
        """Buscar versión inexistente retorna None."""
        repo = ModelVersionRepository(test_db)
        assert repo.get_by_version("v99.0.0") is None

    def test_get_latest(self, test_db):
        """get_latest deve retornar la versión más reciente por training_date."""
        repo = ModelVersionRepository(test_db)

        repo.create(ModelVersionCreate(
            version="v1.0.0",
            training_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ))
        repo.create(ModelVersionCreate(
            version="v2.0.0",
            training_date=datetime(2026, 4, 1, tzinfo=timezone.utc),
        ))

        latest = repo.get_latest()
        assert latest is not None
        assert latest.version == "v2.0.0"

    def test_get_latest_empty(self, test_db):
        """get_latest en BD vacía deve retornar None."""
        repo = ModelVersionRepository(test_db)
        assert repo.get_latest() is None

    def test_update_acceptance_criteria(self, test_db):
        """Actualizar si el modelo cumplió CA-01."""
        repo = ModelVersionRepository(test_db)
        created = repo.create(ModelVersionCreate(
            version="v1.0.0", acceptance_criteria_met=False))

        updated = repo.update(
            created.id,
            ModelVersionUpdate(acceptance_criteria_met=True),
        )
        assert updated is not None
        assert updated.acceptance_criteria_met is True

    def test_delete_version(self, test_db):
        """Eliminar versión de modelo."""
        repo = ModelVersionRepository(test_db)
        created = repo.create(ModelVersionCreate(version="v1.0.0"))

        assert repo.delete(created.id) is True
        assert repo.get_by_version("v1.0.0") is None

    def test_xgboost_params_stores_json(self, test_db):
        """Verificar que xgboost_params se serializa y deserializa correctamente."""
        repo = ModelVersionRepository(test_db)

        params = {
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "subsample": 0.8,
        }
        created = repo.create(ModelVersionCreate(
            version="v3.0.0", xgboost_params=params))

        found = repo.get_by_version("v3.0.0")
        assert found is not None
        assert found.xgboost_params == params
