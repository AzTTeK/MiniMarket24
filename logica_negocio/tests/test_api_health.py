"""
DEMAND-24 — Tests: API Health Endpoint

Verifica el endpoint de salud del sistema.
"""

from fastapi.testclient import TestClient

from logica_negocio.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests para GET /api/v1/health."""

    def test_health_returns_ok(self):
        """El endpoint debe retornar status 200 con 'ok'."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert data["phase"] == 4

    def test_health_response_structure(self):
        """La respuesta debe contener exactamente los campos esperados."""
        response = client.get("/api/v1/health")
        data = response.json()

        expected_keys = {"status", "version", "phase"}
        assert set(data.keys()) == expected_keys
