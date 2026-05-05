"""
DEMAND-24 — Tests: API Alerts Endpoints + Alert Engine

Verifica los endpoints de alertas y el motor de detección de quiebre de stock.
"""

import pytest
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from logica_negocio.core.alert_engine import AlertEngine
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


def _seed_sku_and_prediction(db, sku_code="BEVERAGES", demand=200.0, mape=10.0):
    """Crea un SKU + predicción para testing."""
    sku = Sku(sku_code=sku_code, description=f"Test {sku_code}")
    db.add(sku)
    db.commit()
    db.refresh(sku)

    prediction = Prediction(
        sku_id=sku.id,
        week_start=date(2026, 5, 5),
        predicted_demand=demand,
        mape=mape,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return sku.id, prediction.id


@pytest.fixture(autouse=True)
def setup_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


class TestAlertEngine:
    """Tests para el motor de alertas (RF-04)."""

    def test_stock_break_detected(self):
        """Genera alerta cuando demanda > stock."""
        db = TestSessionLocal()
        sku_id, _ = _seed_sku_and_prediction(db, demand=200.0)

        engine = AlertEngine(db)
        alerts = engine.check_stock_alerts({sku_id: 100})

        assert len(alerts) == 1
        assert "Posible quiebre de stock" in alerts[0].message
        assert alerts[0].alert_type == "stock_break"
        db.close()

    def test_no_alert_when_stock_sufficient(self):
        """Sin alertas cuando stock >= demanda."""
        db = TestSessionLocal()
        sku_id, _ = _seed_sku_and_prediction(db, demand=100.0)

        engine = AlertEngine(db)
        alerts = engine.check_stock_alerts({sku_id: 150})

        assert len(alerts) == 0
        db.close()

    def test_no_alert_empty_stock_levels(self):
        """Sin alertas cuando no se envían niveles de stock."""
        db = TestSessionLocal()

        engine = AlertEngine(db)
        alerts = engine.check_stock_alerts({})

        assert len(alerts) == 0
        db.close()

    def test_alert_message_format(self):
        """El mensaje sigue el formato SRS RF-04."""
        db = TestSessionLocal()
        sku_id, _ = _seed_sku_and_prediction(db, demand=250.0)

        engine = AlertEngine(db)
        alerts = engine.check_stock_alerts({sku_id: 50})

        message = alerts[0].message
        assert "Demanda proyectada: 250 uds" in message
        assert "Stock actual: 50 uds" in message
        db.close()

    def test_low_confidence_alert(self):
        """Genera alerta de baja confianza cuando MAPE > umbral."""
        db = TestSessionLocal()
        _seed_sku_and_prediction(db, sku_code="HIGH_MAPE", demand=100.0, mape=30.0)

        engine = AlertEngine(db)
        alerts = engine.check_low_confidence_alerts(mape_threshold=25.0)

        assert len(alerts) == 1
        assert alerts[0].alert_type == "low_confidence"
        db.close()


class TestAlertEndpoints:
    """Tests para /api/v1/alerts."""

    def test_list_alerts_empty(self, client):
        """Lista vacía sin alertas."""
        response = client.get("/api/v1/alerts")

        assert response.status_code == 200
        assert response.json() == []

    def test_check_stock_creates_alerts(self, client):
        """POST /check-stock genera alertas cuando hay riesgo."""
        db = TestSessionLocal()
        sku_id, _ = _seed_sku_and_prediction(db, demand=300.0)
        db.close()

        response = client.post(
            "/api/v1/alerts/check-stock",
            json={"stock_levels": {str(sku_id): 100}},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_acknowledge_alert(self, client):
        """PATCH acknowledge marca alerta como atendida."""
        db = TestSessionLocal()
        sku_id, _ = _seed_sku_and_prediction(db, demand=500.0)

        engine = AlertEngine(db)
        alerts = engine.check_stock_alerts({sku_id: 10})
        alert_id = alerts[0].id
        db.close()

        response = client.patch(f"/api/v1/alerts/{alert_id}/acknowledge")

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_acknowledge_not_found(self, client):
        """Atender alerta inexistente retorna 404."""
        response = client.patch("/api/v1/alerts/9999/acknowledge")

        assert response.status_code == 404
