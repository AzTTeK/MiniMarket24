"""
DEMAND-24 — Tests para Trainer
Tests unitarios para la clase ModelTrainer.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
from modulo_analitico.training.trainer import ModelTrainer
from modulo_analitico.config.ml_config import MLConfig


def create_sample_weekly_data(n_weeks=52):
    """Crea datos semanales de ejemplo para training."""
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


def test_trainer_initialization():
    """ModelTrainer debe inicializarse correctamente."""
    config = MLConfig()
    trainer = ModelTrainer(config)
    assert trainer is not None, "ModelTrainer no debe ser None"
    assert hasattr(trainer, 'config'), "ModelTrainer debe tener config"
    print("[PASS] test_trainer_initialization")


def test_trainer_train_success():
    """ModelTrainer debe entrenar correctamente."""
    config = MLConfig()
    df = create_sample_weekly_data(n_weeks=52)
    trainer = ModelTrainer(config)
    
    feature_cols = ['year', 'month', 'week_of_year', 'sales_lag_1', 'sales_lag_2', 'sales_rolling_mean_4']
    model, metrics, predictions_df = trainer.train(df, feature_columns=feature_cols, target_col='sales', test_size=0.2)
    
    assert model is not None, "Model no debe ser None"
    assert metrics is not None, "Metrics no debe ser None"
    print("[PASS] test_trainer_train_success")


def test_trainer_metrics_returned():
    """ModelTrainer debe retornar métricas válidas."""
    config = MLConfig()
    df = create_sample_weekly_data(n_weeks=52)
    trainer = ModelTrainer(config)
    
    feature_cols = ['year', 'month', 'week_of_year', 'sales_lag_1', 'sales_lag_2', 'sales_rolling_mean_4']
    model, metrics, predictions_df = trainer.train(df, feature_columns=feature_cols, target_col='sales', test_size=0.2)
    
    assert isinstance(metrics, dict), "Metrics debe ser diccionario"
    print("[PASS] test_trainer_metrics_returned")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de ModelTrainer")
    print("=" * 60)
    
    test_trainer_initialization()
    test_trainer_train_success()
    test_trainer_metrics_returned()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
