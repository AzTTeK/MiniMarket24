"""
DEMAND-24 — Wrappers para Dependencias Externas

Interfaces abstractas para librerías de terceros (XGBoost, pandas, etc.).
Cumple con Regla I: Agnosticismo de Dependencias.
"""

from .xgboost_wrapper import XGBoostModelWrapper

__all__ = ["XGBoostModelWrapper"]
