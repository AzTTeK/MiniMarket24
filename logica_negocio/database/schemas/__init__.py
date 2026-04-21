"""
DEMAND-24 — Database Schemas Package

Exporta todos los DTOs Pydantic para uso en repositories y API.
"""

from .evaluation_fold import EvaluationFoldCreate, EvaluationFoldRead, EvaluationFoldUpdate
from .model_version import ModelVersionCreate, ModelVersionRead, ModelVersionUpdate
from .prediction import PredictionCreate, PredictionRead, PredictionUpdate
from .sku import SkuCreate, SkuRead, SkuUpdate

__all__ = [
    "SkuCreate",
    "SkuRead",
    "SkuUpdate",
    "PredictionCreate",
    "PredictionRead",
    "PredictionUpdate",
    "EvaluationFoldCreate",
    "EvaluationFoldRead",
    "EvaluationFoldUpdate",
    "ModelVersionCreate",
    "ModelVersionRead",
    "ModelVersionUpdate",
]
