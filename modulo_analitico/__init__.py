"""
DEMAND-24 — Módulo Analítico

Sistema Inteligente de Predicción de Demanda para MiniMarket La 24 S.A.S.

Módulo responsable de:
- Carga y validación de datos (RF-01, RF-02)
- Feature engineering
- Entrenamiento de modelos (RF-03)
- Generación de predicciones con intervalos de confianza
- Evaluación con walk-forward validation (CA-01)

Uso:
    from modulo_analitico.predictor import DemandPredictor
    
    predictor = DemandPredictor()
    predictor.load_data()
    predictor.prepare_data()
    predictor.train()
    predictions = predictor.predict(weeks_ahead=4)
"""

from .predictor import DemandPredictor

__version__ = "0.1.0"
__all__ = ["DemandPredictor"]
