"""
DEMAND-24 — Pydantic Schemas: EvaluationFold

DTOs para métricas de evaluación por fold de WalkForward CV.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EvaluationFoldCreate(BaseModel):
    """Schema para crear un registro de evaluación por fold."""

    fold_number: int = Field(..., ge=1, description="Número del fold (1-indexed)")
    sku_id: Optional[int] = Field(None, description="FK al SKU (None = evaluación global)")
    mape: Optional[float] = Field(None, ge=0, description="MAPE del fold")
    mae: Optional[float] = Field(None, ge=0, description="MAE del fold")
    bias: Optional[float] = Field(None, description="Sesgo medio del fold")


class EvaluationFoldRead(BaseModel):
    """Schema para leer un registro de evaluación desde la BD."""

    id: int
    fold_number: int
    sku_id: Optional[int] = None
    mape: Optional[float] = None
    mae: Optional[float] = None
    bias: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EvaluationFoldUpdate(BaseModel):
    """Schema para actualizar métricas de un fold (campos opcionales)."""

    mape: Optional[float] = Field(None, ge=0)
    mae: Optional[float] = Field(None, ge=0)
    bias: Optional[float] = None
