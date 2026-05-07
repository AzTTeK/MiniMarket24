"""
DEMAND-24 — API Router: Training

Endpoint para disparar el re-entrenamiento del modelo de IA.

Cumple con:
- Decisión #12: Backend accede ML SOLO vía DemandPredictor
- Decisión #9: Pipeline lineal (load → aggregate → feature → train → save)
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
        "Dispara el pipeline completo de entrenamiento del modelo XGBoost en segundo plano. "
        "Retorna inmediatamente para evitar timeouts."
    ),
)
def trigger_training(background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> TrainResponse:
    """
    Ejecuta el pipeline de entrenamiento completo de forma asíncrona.
    """
    service = DemandService(db)
    
    # Ejecutamos el entrenamiento en segundo plano
    background_tasks.add_task(service.trigger_training)

    return TrainResponse(
        status="pending",
        message="Sincronización iniciada. El proceso continuará en segundo plano.",
        training_results={}
    )
