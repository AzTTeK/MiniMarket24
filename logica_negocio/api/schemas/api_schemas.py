"""
DEMAND-24 — API Response/Request Schemas

Schemas Pydantic específicos para la capa REST.
Separados de los DB schemas para cumplir Regla VII (contrato de API).

Los DB schemas son el contrato interno (Repository ↔ Service).
Estos schemas son el contrato externo (API ↔ Frontend).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Health ──────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: str = Field(..., description="Estado del sistema ('ok' / 'error')")
    version: str = Field(..., description="Versión del sistema")
    phase: int = Field(..., description="Fase actual del desarrollo")


# ── Training ────────────────────────────────────────────────────

class TrainRequest(BaseModel):
    """Request para disparar entrenamiento (extensible)."""

    sku_ids: Optional[List[int]] = Field(
        None, description="IDs de SKUs específicos (None = todos)"
    )


class TrainResponse(BaseModel):
    """Respuesta del endpoint de entrenamiento."""

    status: str = Field(..., description="Resultado: 'success' / 'error'")
    message: str = Field(..., description="Descripción del resultado")
    training_results: Optional[Dict[str, Any]] = Field(
        None, description="Métricas y resultados del entrenamiento"
    )


# ── Alerts ──────────────────────────────────────────────────────

class StockCheckRequest(BaseModel):
    """Request para verificar alertas de stock."""

    stock_levels: Dict[int, int] = Field(
        ..., description="Niveles de stock: {sku_id: cantidad_actual}"
    )


class AlertAcknowledgeResponse(BaseModel):
    """Respuesta al marcar una alerta como atendida."""

    status: str
    alert_id: int
    message: str


# ── Generic ─────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Respuesta estándar de error."""

    detail: str = Field(..., description="Mensaje descriptivo del error")
    error_code: Optional[str] = Field(None, description="Código interno de error")


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje."""

    status: str
    message: str
