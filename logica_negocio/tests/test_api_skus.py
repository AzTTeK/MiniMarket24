"""
DEMAND-24 — Tests: API SKUs Endpoints

Verifica los endpoints CRUD de SKUs usando BD en memoria.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from logica_negocio.core.database import get_db
from logica_negocio.database.models import Base, Sku, Prediction, Alert  # Explicit imports
from logica_negocio.main import app

# --- Setup: BD en memoria para tests ---
# Usamos StaticPool para mantener la conexión abierta y los datos persistentes en :memory:
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependency get_db con SQLite en memoria."""
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
    """Crea tablas fresh antes de cada test."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


class TestSkuEndpoints:
    """Tests para /api/v1/skus."""

    def test_list_skus_empty(self, client):
        """Lista vacía cuando no hay SKUs."""
        response = client.get("/api/v1/skus")

        assert response.status_code == 200
        assert response.json() == []

    def test_create_sku(self, client):
        """Crear un SKU retorna 201 con datos correctos."""
        response = client.post(
            "/api/v1/skus",
            json={"sku_code": "BEVERAGES", "description": "Bebidas"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["sku_code"] == "BEVERAGES"
        assert data["description"] == "Bebidas"
        assert "id" in data

    def test_create_sku_duplicate(self, client):
        """Crear SKU duplicado retorna 409."""
        client.post(
            "/api/v1/skus",
            json={"sku_code": "DAIRY"},
        )

        response = client.post(
            "/api/v1/skus",
            json={"sku_code": "DAIRY"},
        )

        assert response.status_code == 409

    def test_get_sku_by_id(self, client):
        """Obtener SKU existente retorna 200."""
        create_response = client.post(
            "/api/v1/skus",
            json={"sku_code": "GROCERY_I"},
        )
        sku_id = create_response.json()["id"]

        response = client.get(f"/api/v1/skus/{sku_id}")

        assert response.status_code == 200
        assert response.json()["sku_code"] == "GROCERY_I"

    def test_get_sku_not_found(self, client):
        """SKU inexistente retorna 404."""
        response = client.get("/api/v1/skus/9999")

        assert response.status_code == 404

    def test_list_skus_after_create(self, client):
        """Lista incluye SKUs creados."""
        client.post("/api/v1/skus", json={"sku_code": "MEATS"})
        client.post("/api/v1/skus", json={"sku_code": "EGGS"})

        response = client.get("/api/v1/skus")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
