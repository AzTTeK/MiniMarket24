"""
DEMAND-24 — Métricas de Evaluación

Implementa las métricas de evaluación del modelo: MAPE, MAE, Bias.

Cumple con:
- Regla II: Código Auto-Documentado
- Regla IV: Early Return Pattern
- SRS CA-01: MAPE ≤ 20% en al menos 70% de SKU piloto
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calcula Mean Absolute Percentage Error (MAPE).
    
    Args:
        y_true: Valores reales
        y_pred: Valores predichos
    
    Returns:
        MAPE en porcentaje (ej: 15.5 = 15.5%)
    
    Notes:
        - Maneja ceros en y_true evitando división por cero
        - Retorna 0 si ambos arrays están vacíos
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if len(y_true) == 0 or len(y_pred) == 0:
        return 0.0

    mask = y_true != 0
    if not mask.any():
        return 0.0

    y_true_filtered = y_true[mask]
    y_pred_filtered = y_pred[mask]

    percentage_errors = np.abs((y_true_filtered - y_pred_filtered) / y_true_filtered)

    mape = np.mean(percentage_errors) * 100

    return mape


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calcula Mean Absolute Error (MAE).
    
    Args:
        y_true: Valores reales
        y_pred: Valores predichos
    
    Returns:
        MAE en unidades de producto
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if len(y_true) == 0:
        return 0.0

    mae = np.mean(np.abs(y_true - y_pred))

    return mae


def calculate_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calcula Bias (sesgo sistemático).
    
    Args:
        y_true: Valores reales
        y_pred: Valores predichos
    
    Returns:
        Bias positivo = sobreestimación, negativo = subestimación
    
    Notes:
        - Bias > 0: El modelo tiende a sobreestimar
        - Bias < 0: El modelo tiende a subestimar
        - Bias = 0: Sin sesgo sistemático
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if len(y_true) == 0:
        return 0.0

    bias = np.mean(y_pred - y_true)

    return bias


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, float]:
    """
    Calcula todas las métricas simultáneamente.
    
    Args:
        y_true: Valores reales
        y_pred: Valores predichos
    
    Returns:
        Dict con mape, mae, bias
    """
    return {
        "mape": calculate_mape(y_true, y_pred),
        "mae": calculate_mae(y_true, y_pred),
        "bias": calculate_bias(y_true, y_pred),
    }


def calculate_metrics_by_sku(
    df: pd.DataFrame,
    y_true_col: str = "sales",
    y_pred_col: str = "prediction",
    group_cols: list[str] = None,
) -> pd.DataFrame:
    """
    Calcula métricas por SKU (tienda + familia).
    
    Args:
        df: DataFrame con predicciones y valores reales
        y_true_col: Columna con valores reales
        y_pred_col: Columna con predicciones
        group_cols: Columnas para agrupar (ej: ["store_nbr", "family"])
    
    Returns:
        DataFrame con métricas por SKU
    """
    if group_cols is None:
        group_cols = ["store_nbr", "family"]

    results = []

    for group_values, group_df in df.groupby(group_cols):
        y_true = group_df[y_true_col].values
        y_pred = group_df[y_pred_col].values

        metrics = calculate_metrics(y_true, y_pred)

        result_row = {col: val for col, val in zip(group_cols, group_values)}
        result_row.update(metrics)
        result_row["n_samples"] = len(group_df)

        results.append(result_row)

    metrics_df = pd.DataFrame(results)

    return metrics_df


def evaluate_confidence_level(
    metrics_df: pd.DataFrame,
    mape_threshold: float = 25.0,
) -> Tuple[float, float]:
    """
    Evalúa el nivel de confianza del modelo.
    Implementa RNF-07 (Confiabilidad del Modelo).
    
    Args:
        metrics_df: DataFrame con métricas por SKU
        mape_threshold: Umbral de MAPE para baja confianza
    
    Returns:
        Tuple con (porcentaje_alta_confianza, porcentaje_baja_confianza)
    """
    if len(metrics_df) == 0:
        return 0.0, 0.0

    n_total = len(metrics_df)
    n_low_confidence = (metrics_df["mape"] > mape_threshold).sum()
    n_high_confidence = n_total - n_low_confidence

    pct_high = (n_high_confidence / n_total) * 100
    pct_low = (n_low_confidence / n_total) * 100

    return pct_high, pct_low


def check_acceptance_criteria(
    metrics_df: pd.DataFrame,
    target_mape: float = 20.0,
    target_pct_skus: float = 70.0,
    mape_threshold: float = 25.0,
) -> Tuple[bool, str]:
    """
    Verifica si se cumplen los criterios de aceptación CA-01.
    
    Args:
        metrics_df: DataFrame con métricas por SKU
        target_mape: MAPE objetivo (≤ 20%)
        target_pct_skus: Porcentaje de SKU que deben cumplir (≥ 70%)
        mape_threshold: Umbral para baja confianza
    
    Returns:
        Tuple con (cumple_criterio, mensaje_explicativo)
    
    Criteria (CA-01):
        - MAPE ≤ 20% en al menos el 70% de los SKU piloto
    """
    if len(metrics_df) == 0:
        return False, "No hay datos para evaluar"

    n_total = len(metrics_df)
    n_acceptable = (metrics_df["mape"] <= target_mape).sum()
    pct_acceptable = (n_acceptable / n_total) * 100

    cumple = pct_acceptable >= target_pct_skus

    if cumple:
        mensaje = (
            f"CRITERIO CUMPLIDO (CA-01): {pct_acceptable:.1f}% de SKU tienen MAPE ≤ {target_mape}%. "
            f"Requerido: ≥ {target_pct_skus}%. "
            f"MAPE promedio: {metrics_df['mape'].mean():.2f}%"
        )
    else:
        mensaje = (
            f"CRITERIO NO CUMPLIDO (CA-01): {pct_acceptable:.1f}% de SKU tienen MAPE ≤ {target_mape}%. "
            f"Requerido: ≥ {target_pct_skus}%. "
            f"MAPE promedio: {metrics_df['mape'].mean():.2f}%. "
            f"SKU con baja confianza: {(metrics_df['mape'] > mape_threshold).sum()} de {n_total}"
        )

    return cumple, mensaje
