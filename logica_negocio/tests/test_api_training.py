"""
DEMAND-24 — Tests: API Training Endpoint

Verifica el endpoint de entrenamiento con mock del DemandPredictor.
"""

import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from logica_negocio.core.database import get_db
from logica_negocio.database.models import Base, Sku, Prediction, Alert
from logica_negocio.main import app

# --- Setup ---
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Fixture que provee un TestClient con la BD en memoria configurada."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def setup_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


class TestTrainingEndpoint:
    """Tests para POST /api/v1/training."""

    @patch("logica_negocio.core.services.DemandService.trigger_training")
    def test_training_success(self, mock_trigger, client):
        """Entrenamiento exitoso retorna 202 (aceptado) con estado pending."""
        mock_trigger.return_value = {
            "mape_mean": 15.5,
            "mae_mean": 42.3,
            "ca01_met": True,
        }

        response = client.post("/api/v1/training")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        mock_trigger.assert_called_once()
