"""
DEMAND-24 — API Router: Predictions

Endpoints para consulta de predicciones de demanda.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import ErrorResponse
from logica_negocio.core.database import get_db
from logica_negocio.core.services import DemandService
from logica_negocio.database.schemas.prediction import PredictionRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get(
    "",
    response_model=List[PredictionRead],
    summary="Listar todas las predicciones",
    description="Obtiene todas las predicciones generadas por el sistema.",
)
def list_predictions(db: Session = Depends(get_db)) -> List[PredictionRead]:
    """Lista todas las predicciones del sistema."""
    service = DemandService(db)
    return service.get_all_predictions()


@router.get(
    "/{sku_id}",
    response_model=List[PredictionRead],
    summary="Predicciones por SKU",
    description="Obtiene todas las predicciones de un SKU específico, ordenadas por semana.",
    responses={404: {"model": ErrorResponse}},
)
def get_predictions_by_sku(
    sku_id: int,
    db: Session = Depends(get_db),
) -> List[PredictionRead]:
    """
    Obtiene predicciones de un SKU incluyendo intervalos de confianza.

    Cada predicción contiene:
    - predicted_demand: demanda estimada
    - lower_bound / upper_bound: CI al 90%
    - mape: error del modelo para ese SKU
    - confidence_level: HIGH / LOW según RNF-07
    """
    service = DemandService(db)

    # Verificar que el SKU existe
    sku = service.get_sku_by_id(sku_id)
    if sku is None:
        raise HTTPException(
            status_code=404,
            detail=f"SKU con id={sku_id} no encontrado",
        )

    predictions = service.get_predictions_by_sku(sku_id)
    return predictions
