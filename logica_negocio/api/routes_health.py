"""
DEMAND-24 — API Router: Health

Endpoint de verificación de salud del sistema.
"""

from fastapi import APIRouter

from logica_negocio.api.schemas.api_schemas import HealthResponse

router = APIRouter(tags=["Health"])

APP_VERSION = "0.1.0"
APP_PHASE = 4


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Estado del sistema",
    description="Verifica que el servidor esté operativo.",
)
def health_check() -> HealthResponse:
    """Retorna el estado actual del sistema DEMAND-24."""
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        phase=APP_PHASE,
    )
