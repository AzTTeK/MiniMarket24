"""
DEMAND-24 — Tests para XGBoost Wrapper
Tests unitarios para las interfaces abstractas del wrapper XGBoost.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
from modulo_analitico.wrappers.xgboost_wrapper import XGBoostModelWrapper
from modulo_analitico.config.ml_config import MLConfig


def create_sample_features(n_samples=100, n_features=10):
    """Crea conjunto de características de ejemplo."""
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(10, 100, n_samples)
    return X, y


def test_xgboost_wrapper_initialization():
    """XGBoostModelWrapper debe inicializarse correctamente."""
    config = MLConfig()
    wrapper = XGBoostModelWrapper(n_estimators=100, max_depth=5, random_state=42)
    assert wrapper is not None, "Wrapper no debe ser None"
    print("[PASS] test_xgboost_wrapper_initialization")


def test_xgboost_wrapper_fit():
    """XGBoostModelWrapper debe entrenar correctamente."""
    config = MLConfig()
    X, y = create_sample_features(n_samples=100, n_features=10)
    wrapper = XGBoostModelWrapper(n_estimators=50, max_depth=5, random_state=42)
    wrapper.fit(X, y)
    assert wrapper._is_fitted == True, "Wrapper debe estar marcado como fitted"
    assert wrapper._model is not None, "Wrapper debe tener modelo"
    print("[PASS] test_xgboost_wrapper_fit")


def test_xgboost_wrapper_predict():
    """XGBoostModelWrapper debe hacer predicciones."""
    config = MLConfig()
    X_train, y_train = create_sample_features(n_samples=100, n_features=10)
    X_test = np.random.randn(20, 10)
    wrapper = XGBoostModelWrapper(n_estimators=50, max_depth=5, random_state=42)
    wrapper.fit(X_train, y_train)
    predictions = wrapper.predict(X_test)
    assert predictions is not None, "Predictions no debe ser None"
    assert len(predictions) == len(X_test), "Debe haber predicción por muestra"
    print("[PASS] test_xgboost_wrapper_predict")


def test_xgboost_wrapper_feature_importance():
    """XGBoostModelWrapper debe retornar importancia."""
    config = MLConfig()
    X_train, y_train = create_sample_features(n_samples=100, n_features=10)
    wrapper = XGBoostModelWrapper(n_estimators=50, max_depth=5, random_state=42)
    wrapper.fit(X_train, y_train)
    importance = wrapper.feature_importances()
    assert importance is not None, "Importance no debe ser None"
    assert len(importance) == 10, "Debe haber importancia para cada feature"
    print("[PASS] test_xgboost_wrapper_feature_importance")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de XGBoost Wrapper")
    print("=" * 60)
    
    test_xgboost_wrapper_initialization()
    test_xgboost_wrapper_fit()
    test_xgboost_wrapper_predict()
    test_xgboost_wrapper_feature_importance()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
