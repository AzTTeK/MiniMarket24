"""
DEMAND-24 — Pydantic Schemas: Prediction

DTOs para creación, lectura y actualización de predicciones de demanda.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    """Schema para crear una nueva predicción."""

    sku_id: int = Field(..., description="FK al SKU")
    week_start: date = Field(..., description="Inicio de la semana predicha")
    predicted_demand: float = Field(..., ge=0, description="Demanda estimada")
    confidence_level: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Nivel de confianza (0-1)"
    )
    lower_bound: Optional[float] = Field(None, description="Límite inferior CI")
    upper_bound: Optional[float] = Field(None, description="Límite superior CI")
    mape: Optional[float] = Field(None, ge=0, description="MAPE del SKU")


class PredictionRead(BaseModel):
    """Schema para leer una predicción desde la BD."""

    id: int
    sku_id: int
    week_start: date
    predicted_demand: float
    confidence_level: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    mape: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PredictionUpdate(BaseModel):
    """Schema para actualizar una predicción (campos opcionales)."""

    predicted_demand: Optional[float] = Field(None, ge=0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    mape: Optional[float] = Field(None, ge=0)
