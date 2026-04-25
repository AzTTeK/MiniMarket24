"""
DEMAND-24 — Tests de Refuerzo para Cobertura en Código Nuevo (v2)
Objetivo: Lograr >80% en xgboost_wrapper.py.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from modulo_analitico.wrappers.xgboost_wrapper import XGBoostModelWrapper

def test_xgboost_wrapper_full_coverage(tmp_path):
    """Cubre todas las rutas lógicas del wrapper."""
    wrapper = XGBoostModelWrapper(n_estimators=10)
    
    X = np.random.rand(10, 5)
    y = np.random.rand(10)
    
    # 1. Error antes de fit
    with pytest.raises(RuntimeError):
        wrapper.predict(X)
    with pytest.raises(RuntimeError):
        wrapper.predict_with_quantiles(X)
    with pytest.raises(RuntimeError):
        wrapper.save(tmp_path / "model.json")
    assert wrapper.feature_importances() is None

    # 2. Fit
    wrapper.fit(X, y)
    assert wrapper._is_fitted
    assert wrapper.feature_importances() is not None

    # 3. Predict
    preds = wrapper.predict(X)
    assert len(preds) == 10
    
    median, lower, upper = wrapper.predict_with_quantiles(X)
    assert len(median) == 10
    assert np.all(lower < upper)

    # 4. Save & Load
    model_path = tmp_path / "model.json"
    wrapper.save(model_path)
    assert model_path.exists()

    new_wrapper = XGBoostModelWrapper()
    new_wrapper.load(model_path)
    assert new_wrapper._is_fitted
    
    # 5. Load error (File not found)
    with pytest.raises(FileNotFoundError):
        new_wrapper.load(tmp_path / "non_existent.json")

def test_xgboost_init_params():
    """Valida la asignación de parámetros en init."""
    wrapper = XGBoostModelWrapper(max_depth=3, learning_rate=0.05)
    assert wrapper.max_depth == 3
    assert wrapper.learning_rate == 0.05
