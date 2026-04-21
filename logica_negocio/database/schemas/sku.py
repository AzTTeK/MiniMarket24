"""
DEMAND-24 — Pydantic Schemas: Sku

DTOs para creación, lectura y actualización de SKUs.
Contrato entre Backend y Frontend (Regla VII).
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkuCreate(BaseModel):
    """Schema para crear un nuevo SKU."""

    sku_code: str = Field(..., max_length=20, description="Código único del SKU")
    description: Optional[str] = Field(None, description="Descripción del producto")


class SkuRead(BaseModel):
    """Schema para leer un SKU desde la BD."""

    id: int
    sku_code: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SkuUpdate(BaseModel):
    """Schema para actualizar un SKU (campos opcionales)."""

    sku_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
