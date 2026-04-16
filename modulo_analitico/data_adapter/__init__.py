"""
DEMAND-24 — Adaptador de Datos

Módulo responsable de cargar, validar, agregar y transformar los datos
del dataset Kaggle al esquema de MiniMarket 24.

Cumple con Regla I: Separación Estricta de Responsabilidades.
"""

from .loader import DataLoader
from .aggregator import DataAggregator
from .feature_builder import FeatureBuilder

__all__ = ["DataLoader", "DataAggregator", "FeatureBuilder"]
