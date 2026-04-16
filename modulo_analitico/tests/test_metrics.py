"""
DEMAND-24 — Tests para Métricas

Tests unitarios para las funciones de evaluación del modelo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd

from modulo_analitico.models.metrics import (
    calculate_mape,
    calculate_mae,
    calculate_bias,
    calculate_metrics,
    check_acceptance_criteria,
)


def test_mape_perfect_prediction():
    """MAPE debe ser 0% para predicciones perfectas."""
    y_true = np.array([10, 20, 30, 40])
    y_pred = np.array([10, 20, 30, 40])
    mape = calculate_mape(y_true, y_pred)
    assert mape == 0.0, f"MAPE deberia ser 0%, obtuvo {mape}%"
    print("[PASS] test_mape_perfect_prediction")


def test_mape_ten_percent_error():
    """MAPE debe ser 10% con error constante del 10%."""
    y_true = np.array([100, 200, 300])
    y_pred = np.array([110, 220, 330])
    mape = calculate_mape(y_true, y_pred)
    assert abs(mape - 10.0) < 0.01, f"MAPE deberia ser 10%, obtuvo {mape}%"
    print("[PASS] test_mape_ten_percent_error")


def test_mape_with_zeros():
    """MAPE debe manejar ceros en y_true correctamente."""
    y_true = np.array([0, 100, 200])
    y_pred = np.array([10, 110, 220])
    mape = calculate_mape(y_true, y_pred)
    assert mape > 0, "MAPE deberia ser > 0"
    print("[PASS] test_mape_with_zeros")


def test_mae_calculation():
    """MAE debe calcular el error absoluto medio correctamente."""
    y_true = np.array([10, 20, 30])
    y_pred = np.array([12, 18, 33])
    mae = calculate_mae(y_true, y_pred)
    expected_mae = (2 + 2 + 3) / 3
    assert abs(mae - expected_mae) < 0.01, f"MAE deberia ser {expected_mae}, obtuvo {mae}"
    print("[PASS] test_mae_calculation")


def test_bias_overestimation():
    """Bias positivo indica sobreestimación."""
    y_true = np.array([10, 20, 30])
    y_pred = np.array([15, 25, 35])
    bias = calculate_bias(y_true, y_pred)
    assert bias > 0, f"Bias deberia ser positivo (sobreestimacion), obtuvo {bias}"
    print("[PASS] test_bias_overestimation")


def test_bias_underestimation():
    """Bias negativo indica subestimación."""
    y_true = np.array([10, 20, 30])
    y_pred = np.array([8, 18, 28])
    bias = calculate_bias(y_true, y_pred)
    assert bias < 0, f"Bias deberia ser negativo (subestimacion), obtuvo {bias}"
    print("[PASS] test_bias_underestimation")


def test_calculate_metrics_all_in_one():
    """calculate_metrics debe retornar dict con mape, mae, bias."""
    y_true = np.array([100, 200, 300])
    y_pred = np.array([110, 190, 320])
    metrics = calculate_metrics(y_true, y_pred)
    assert "mape" in metrics, "metrics debe contener 'mape'"
    assert "mae" in metrics, "metrics debe contener 'mae'"
    assert "bias" in metrics, "metrics debe contener 'bias'"
    assert metrics["mape"] > 0, "MAPE deberia ser > 0"
    print("[PASS] test_calculate_metrics_all_in_one")


def test_check_acceptance_criteria_pass():
    """Criterio CA-01 debe pasar con 70%+ de SKU con MAPE ≤ 20%."""
    metrics_df = pd.DataFrame({
        "store_nbr": [1, 2, 3, 4, 5],
        "family": ["A", "B", "C", "D", "E"],
        "mape": [15.0, 18.0, 12.0, 25.0, 19.0],
    })
    cumple, mensaje = check_acceptance_criteria(metrics_df, target_mape=20.0, target_pct_skus=70.0)
    assert cumple == True, f"Deberia cumplir CA-01. {mensaje}"
    print("[PASS] test_check_acceptance_criteria_pass")


def test_check_acceptance_criteria_fail():
    """Criterio CA-01 debe fallar con < 70% de SKU con MAPE ≤ 20%."""
    metrics_df = pd.DataFrame({
        "store_nbr": [1, 2, 3, 4, 5],
        "family": ["A", "B", "C", "D", "E"],
        "mape": [25.0, 28.0, 12.0, 30.0, 22.0],
    })
    cumple, mensaje = check_acceptance_criteria(metrics_df, target_mape=20.0, target_pct_skus=70.0)
    assert cumple == False, f"Deberia NO cumplir CA-01. {mensaje}"
    print("[PASS] test_check_acceptance_criteria_fail")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de Métricas")
    print("=" * 60)
    
    test_mape_perfect_prediction()
    test_mape_ten_percent_error()
    test_mape_with_zeros()
    test_mae_calculation()
    test_bias_overestimation()
    test_bias_underestimation()
    test_calculate_metrics_all_in_one()
    test_check_acceptance_criteria_pass()
    test_check_acceptance_criteria_fail()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
