"""
DEMAND-24 — API Router: Training

Endpoint para disparar el re-entrenamiento del modelo de IA.

Cumple con:
- Decisión #12: Backend accede ML SOLO vía DemandPredictor
- Decisión #9: Pipeline lineal (load → aggregate → feature → train → save)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import TrainResponse
from logica_negocio.core.database import get_db
from logica_negocio.core.services import DemandService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["Training"])


@router.post(
    "",
    response_model=TrainResponse,
    summary="Entrenar modelo",
    description=(
        "Dispara el pipeline completo de entrenamiento del modelo XGBoost. "
        "Ejecuta: load_data → prepare_data → train → save_to_db. "
        "Retorna métricas del entrenamiento incluyendo cumplimiento de CA-01."
    ),
)
def trigger_training(db: Session = Depends(get_db)) -> TrainResponse:
    """
    Ejecuta el pipeline de entrenamiento completo.

    Este endpoint:
    1. Carga datos desde data/raw/ (CSVs de Kaggle)
    2. Agrega a nivel semanal y genera features
    3. Entrena el modelo XGBoost con TimeSeriesSplit
    4. Persiste modelo, métricas y predicciones en BD

    Returns:
        TrainResponse con estado y métricas del entrenamiento.
    """
    service = DemandService(db)

    try:
        training_results = service.trigger_training()
    except RuntimeError as err:
        logger.error("Entrenamiento falló: %s", err)
        raise HTTPException(status_code=500, detail=str(err))

    return TrainResponse(
        status="success",
        message="Modelo entrenado y persistido exitosamente",
        training_results=training_results,
    )
