"""
DEMAND-24 — API Package

Routers REST para la interfaz pública del backend.
"""

from .routes_alerts import router as alerts_router
from .routes_health import router as health_router
from .routes_predictions import router as predictions_router
from .routes_skus import router as skus_router
from .routes_training import router as training_router

__all__ = [
    "alerts_router",
    "health_router",
    "predictions_router",
    "skus_router",
    "training_router",
]
