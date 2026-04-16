"""
DEMAND-24 — Tests para Predictor (API Pública)
Tests unitarios para DemandPredictor.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from modulo_analitico.predictor import DemandPredictor
from modulo_analitico.config.ml_config import MLConfig


def test_predictor_initialization():
    """DemandPredictor debe inicializarse correctamente."""
    config = MLConfig()
    predictor = DemandPredictor(config)
    assert predictor is not None, "DemandPredictor no debe ser None"
    assert hasattr(predictor, 'config'), "DemandPredictor debe tener config"
    print("[PASS] test_predictor_initialization")


def test_predictor_has_trainer():
    """DemandPredictor debe tener acceso a entrenador."""
    config = MLConfig()
    predictor = DemandPredictor(config)
    assert hasattr(predictor, 'trainer') or hasattr(predictor, '_trainer'), "Debe tener trainer"
    print("[PASS] test_predictor_has_trainer")


def test_predictor_config_accessible():
    """DemandPredictor config debe ser accesible."""
    config = MLConfig()
    predictor = DemandPredictor(config)
    assert predictor.config is not None, "Config debe ser accesible"
    print("[PASS] test_predictor_config_accessible")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de DemandPredictor (API Pública)")
    print("=" * 60)
    
    test_predictor_initialization()
    test_predictor_has_trainer()
    test_predictor_config_accessible()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
