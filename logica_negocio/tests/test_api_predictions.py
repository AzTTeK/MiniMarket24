"""
DEMAND-24 — Tests: API Predictions Endpoints

Verifica los endpoints de consulta de predicciones.
"""

import pytest
from unittest.mock import patch, MagicMock

from datetime import date
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


def _seed_data():
    """Inserta datos de prueba: 1 SKU + 2 predicciones."""
    db = TestSessionLocal()

    sku = Sku(sku_code="PRODUCE", description="Productos frescos")
    db.add(sku)
    db.commit()
    db.refresh(sku)

    predictions = [
        Prediction(
            sku_id=sku.id,
            week_start=date(2026, 4, 28),
            predicted_demand=150.00,
            confidence_level=0.90,
            lower_bound=135.00,
            upper_bound=165.00,
            mape=12.5,
        ),
        Prediction(
            sku_id=sku.id,
            week_start=date(2026, 5, 5),
            predicted_demand=175.00,
            confidence_level=0.90,
            lower_bound=157.50,
            upper_bound=192.50,
            mape=15.0,
        ),
    ]
    db.add_all(predictions)
    db.commit()
    sku_id = sku.id
    db.close()

    return sku_id


@pytest.fixture(autouse=True)
def setup_tables():
    """Crea tablas fresh antes de cada test."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


class TestPredictionEndpoints:
    """Tests para /api/v1/predictions."""

    def test_list_predictions_empty(self, client):
        """Lista vacía sin predicciones."""
        response = client.get("/api/v1/predictions")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_predictions_by_sku(self, client):
        """Obtiene predicciones de un SKU con datos correctos."""
        sku_id = _seed_data()

        response = client.get(f"/api/v1/predictions/{sku_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["predicted_demand"] == 150.00
        assert data[0]["lower_bound"] == 135.00
        assert data[0]["upper_bound"] == 165.00

    def test_get_predictions_sku_not_found(self, client):
        """SKU inexistente retorna 404."""
        response = client.get("/api/v1/predictions/9999")

        assert response.status_code == 404

    def test_predictions_ordered_by_week(self, client):
        """Predicciones vienen ordenadas por week_start."""
        sku_id = _seed_data()

        response = client.get(f"/api/v1/predictions/{sku_id}")

        data = response.json()
        dates = [d["week_start"] for d in data]
        assert dates == sorted(dates)
