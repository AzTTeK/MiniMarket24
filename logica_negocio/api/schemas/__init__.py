"""
DEMAND-24 — API Schemas Package

Exporta los schemas de request/response de la capa REST.
"""

from .api_schemas import (
    AlertAcknowledgeResponse,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    StockCheckRequest,
    TrainRequest,
    TrainResponse,
)

__all__ = [
    "AlertAcknowledgeResponse",
    "ErrorResponse",
    "HealthResponse",
    "MessageResponse",
    "StockCheckRequest",
    "TrainRequest",
    "TrainResponse",
]
