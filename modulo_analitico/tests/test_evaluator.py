"""
DEMAND-24 — Tests para Evaluator
Tests unitarios para WalkForwardEvaluator.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from modulo_analitico.training.evaluator import WalkForwardEvaluator
from modulo_analitico.config.ml_config import MLConfig


def create_sample_weekly_data(n_weeks=104):
    """Crea datos semanales de ejemplo para evaluación."""
    data = []
    for week in range(n_weeks):
        date = pd.Timestamp("2023-01-02") + pd.Timedelta(weeks=week)
        data.append({
            "sales": np.random.randint(100, 500),
            "year": date.year,
            "month": date.month,
            "week_of_year": date.isocalendar()[1],
            "sales_lag_1": np.random.randint(100, 500),
            "sales_lag_2": np.random.randint(100, 500),
            "sales_rolling_mean_4": np.random.randint(100, 500),
        })
    return pd.DataFrame(data)


def test_evaluator_initialization():
    """WalkForwardEvaluator debe inicializarse correctamente."""
    config = MLConfig()
    evaluator = WalkForwardEvaluator(config)
    assert evaluator is not None, "WalkForwardEvaluator no debe ser None"
    print("[PASS] test_evaluator_initialization")


def test_evaluator_walk_forward():
    """WalkForwardEvaluator debe ejecutar walk-forward validation."""
    config = MLConfig()
    df = create_sample_weekly_data(n_weeks=104)
    evaluator = WalkForwardEvaluator(config)
    
    feature_cols = ['year', 'month', 'week_of_year', 'sales_lag_1', 'sales_lag_2', 'sales_rolling_mean_4']
    
    results = evaluator.evaluate_walk_forward(df, feature_columns=feature_cols, target_col='sales', n_folds=3, min_train_size=50)
    
    assert results is not None, "Results no debe ser None"
    assert isinstance(results, dict), "Results debe ser diccionario"
    print("[PASS] test_evaluator_walk_forward")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de WalkForwardEvaluator")
    print("=" * 60)
    
    test_evaluator_initialization()
    test_evaluator_walk_forward()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
