"""
DEMAND-24 — Core Package

Infraestructura central: base de datos, servicios y motor de alertas.
"""

from .database import get_db
from .services import DemandService

__all__ = ["get_db", "DemandService"]
