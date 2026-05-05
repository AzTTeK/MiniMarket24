"""
DEMAND-24 — API Router: Alerts

Endpoints para consulta y gestión de alertas.
Implementa la interfaz REST para RF-04 (Alertas de Quiebre de Stock).
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import (
    AlertAcknowledgeResponse,
    ErrorResponse,
    StockCheckRequest,
)
from logica_negocio.core.database import get_db
from logica_negocio.core.services import DemandService
from logica_negocio.database.schemas.alert import AlertRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get(
    "",
    response_model=List[AlertRead],
    summary="Listar alertas activas",
    description="Obtiene todas las alertas no atendidas del sistema.",
)
def list_active_alerts(db: Session = Depends(get_db)) -> List[AlertRead]:
    """Lista alertas activas (no atendidas), más recientes primero."""
    service = DemandService(db)
    return service.get_active_alerts()


@router.get(
    "/all",
    response_model=List[AlertRead],
    summary="Listar todas las alertas",
    description="Obtiene todas las alertas (activas y atendidas).",
)
def list_all_alerts(db: Session = Depends(get_db)) -> List[AlertRead]:
    """Lista todas las alertas del sistema."""
    service = DemandService(db)
    return service.get_all_alerts()


@router.get(
    "/sku/{sku_id}",
    response_model=List[AlertRead],
    summary="Alertas por SKU",
    description="Obtiene todas las alertas de un SKU específico.",
)
def get_alerts_by_sku(
    sku_id: int,
    db: Session = Depends(get_db),
) -> List[AlertRead]:
    """Obtiene alertas de un SKU específico."""
    service = DemandService(db)
    return service.get_alerts_by_sku(sku_id)


@router.patch(
    "/{alert_id}/acknowledge",
    response_model=AlertAcknowledgeResponse,
    summary="Atender alerta",
    description="Marca una alerta como atendida por el administrador.",
    responses={404: {"model": ErrorResponse}},
)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
) -> AlertAcknowledgeResponse:
    """Marca una alerta como atendida (is_acknowledged = True)."""
    service = DemandService(db)
    alert = service.acknowledge_alert(alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail=f"Alerta con id={alert_id} no encontrada",
        )

    return AlertAcknowledgeResponse(
        status="success",
        alert_id=alert_id,
        message="Alerta marcada como atendida",
    )


@router.post(
    "/check-stock",
    response_model=List[AlertRead],
    summary="Verificar quiebre de stock",
    description=(
        "Compara niveles de stock actuales contra predicciones de demanda. "
        "Genera alertas para SKUs donde demanda > stock (RF-04)."
    ),
)
def check_stock_alerts(
    request: StockCheckRequest,
    db: Session = Depends(get_db),
) -> List[AlertRead]:
    """
    Ejecuta el motor de alertas para detectar quiebres de stock.

    Body:
        stock_levels: {sku_id: cantidad_actual}

    Returns:
        Lista de alertas generadas.
    """
    service = DemandService(db)
    return service.check_stock_alerts(request.stock_levels)
