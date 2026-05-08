"""
DEMAND-24 — API Router: Dashboard

Endpoint que consolida toda la informacion para el dashboard del frontend.
Retorna KPIs, lista de productos con estados y datos para graficos.
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import DashboardSummary
from logica_negocio.core.database import get_db
from logica_negocio.core.services import DemandService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Resumen completo del dashboard",
    description=(
        "Retorna KPIs, lista de productos con estado de stock, "
        "y datos para graficos de demanda historica vs proyectada."
    ),
)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    """Genera el resumen completo del dashboard a partir de datos en BD."""
    service = DemandService(db)
    return service.get_dashboard_summary()
