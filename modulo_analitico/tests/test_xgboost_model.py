"""
DEMAND-24 — Tests para XGBoost Model
Tests unitarios para XGBoostDemandModel.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from modulo_analitico.models.xgboost_model import XGBoostDemandModel
from modulo_analitico.config.ml_config import MLConfig


def create_sample_features(n_samples=100):
    """Crea conjunto de características de ejemplo."""
    df = pd.DataFrame({
        'sales': np.random.randint(10, 100, n_samples),
        'year': np.random.randint(2023, 2025, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'week_of_year': np.random.randint(1, 53, n_samples),
        'sales_lag_1': np.random.randint(10, 100, n_samples),
        'sales_lag_2': np.random.randint(10, 100, n_samples),
        'sales_rolling_mean_4': np.random.randint(10, 100, n_samples),
    })
    return df


def test_xgboost_model_initialization():
    """XGBoostDemandModel debe inicializarse correctamente."""
    config = MLConfig()
    model = XGBoostDemandModel(config)
    assert model is not None, "Model no debe ser None"
    print("[PASS] test_xgboost_model_initialization")


def test_xgboost_model_fit():
    """XGBoostDemandModel debe entrenar correctamente."""
    config = MLConfig()
    df = create_sample_features(n_samples=100)
    model = XGBoostDemandModel(config)
    feature_cols = ['year', 'month', 'week_of_year', 'sales_lag_1', 'sales_lag_2', 'sales_rolling_mean_4']
    
    result = model.fit(df, feature_columns=feature_cols, target_col='sales')
    
    assert model._is_fitted == True, "Model debe estar entrenado"
    print("[PASS] test_xgboost_model_fit")


def test_xgboost_model_predict():
    """XGBoostDemandModel debe hacer predicciones."""
    config = MLConfig()
    df_train = create_sample_features(n_samples=100)
    df_test = create_sample_features(n_samples=20)
    feature_cols = ['year', 'month', 'week_of_year', 'sales_lag_1', 'sales_lag_2', 'sales_rolling_mean_4']
    
    model = XGBoostDemandModel(config)
    model.fit(df_train, feature_columns=feature_cols, target_col='sales')
    predictions = model.predict(df_test[feature_cols])
    
    assert predictions is not None, "Predictions no debe ser None"
    assert len(predictions) == len(df_test), "Debe haber predicción por muestra"
    print("[PASS] test_xgboost_model_predict")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de XGBoostDemandModel")
    print("=" * 60)
    
    test_xgboost_model_initialization()
    test_xgboost_model_fit()
    test_xgboost_model_predict()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
