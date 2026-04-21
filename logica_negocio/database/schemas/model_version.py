"""
DEMAND-24 — Pydantic Schemas: ModelVersion

DTOs para metadata de versiones de modelos entrenados.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ModelVersionCreate(BaseModel):
    """Schema para registrar una nueva versión de modelo."""

    version: str = Field(..., max_length=20, description="Versión semántica (e.g. 'v1.0.0')")
    training_date: Optional[datetime] = Field(None, description="Fecha de entrenamiento")
    random_seed: Optional[int] = Field(None, description="Semilla de reproducibilidad")
    n_splits: Optional[int] = Field(None, ge=1, description="Número de folds CV")
    xgboost_params: Optional[dict[str, Any]] = Field(
        None, description="Hiperparámetros XGBoost como dict"
    )
    acceptance_criteria_met: Optional[bool] = Field(
        None, description="¿Cumplió CA-01?"
    )


class ModelVersionRead(BaseModel):
    """Schema para leer una versión de modelo desde la BD."""

    id: int
    version: str
    training_date: Optional[datetime] = None
    random_seed: Optional[int] = None
    n_splits: Optional[int] = None
    xgboost_params: Optional[dict[str, Any]] = None
    acceptance_criteria_met: Optional[bool] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ModelVersionUpdate(BaseModel):
    """Schema para actualizar metadata de un modelo (campos opcionales)."""

    training_date: Optional[datetime] = None
    random_seed: Optional[int] = None
    n_splits: Optional[int] = Field(None, ge=1)
    xgboost_params: Optional[dict[str, Any]] = None
    acceptance_criteria_met: Optional[bool] = None
