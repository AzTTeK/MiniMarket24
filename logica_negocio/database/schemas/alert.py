"""
DEMAND-24 — Pydantic Schemas: Alert

DTOs para creación, lectura y actualización de alertas de quiebre de stock.
Implementa RF-04 del SRS.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    """Schema para crear una nueva alerta."""

    sku_id: int = Field(..., description="FK al SKU")
    prediction_id: Optional[int] = Field(None, description="FK a la predicción que originó la alerta")
    alert_type: str = Field(
        ...,
        max_length=30,
        description="Tipo: 'stock_break', 'low_confidence', 'data_quality'",
    )
    message: str = Field(..., description="Mensaje descriptivo de la alerta")
    is_acknowledged: bool = Field(default=False, description="¿Fue atendida?")


class AlertRead(BaseModel):
    """Schema para leer una alerta desde la BD."""

    id: int
    sku_id: int
    prediction_id: Optional[int] = None
    alert_type: str
    message: str
    is_acknowledged: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    """Schema para actualizar una alerta (marcar como atendida)."""

    is_acknowledged: Optional[bool] = None
