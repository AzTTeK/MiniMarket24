"""
DEMAND-24 — Evaluación con Walk-Forward Validation

Implementa validación temporal walk-forward para evaluación robusta.

Cumple con:
- Regla VI: Anti-Leakage (walk-forward estricto)
- SRS CA-01: MAPE ≤ 20% en 70% de SKU piloto
- RNF-07: Confiabilidad del Modelo
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np

from ..config.ml_config import MLConfig
from ..models.xgboost_model import XGBoostDemandModel
from ..models.metrics import (
    calculate_metrics,
    calculate_metrics_by_sku,
    evaluate_confidence_level,
    check_acceptance_criteria,
)


class WalkForwardEvaluator:
    """
    Evaluación walk-forward para series temporales.
    
    Responsabilidades:
    - Implementar walk-forward validation estricto
    - Evaluar modelo en múltiples períodos de test
    - Calcular métricas por SKU y globales
    - Verificar criterios de aceptación (CA-01)
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()

    def evaluate_walk_forward(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        n_folds: int = 5,
        min_train_size: int = 50,
        step_size: int = 1,
    ) -> Dict:
        """
        Ejecuta walk-forward validation.
        
        Args:
            df: DataFrame ordenado por fecha
            feature_columns: Features a usar
            target_col: Columna target
            n_folds: Número de folds de validación
            min_train_size: Mínimo de muestras para train
            step_size: Cuántas muestras avanzar por fold
        
        Returns:
            Dict con resultados completos de evaluación
        
        Notes:
            - Fold 1: train=[0:min_train], test=[min_train:min_train+step]
            - Fold 2: train=[0:min_train+step], test=[min_train+step:min_train+2*step]
            - ...
        """
        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=feature_columns + [target_col])

        if len(df_clean) < min_train_size + step_size:
            raise ValueError(
                f"Datos insuficientes: {len(df_clean)} filas. "
                f"Se requieren al menos {min_train_size + step_size}."
            )

        fold_results = []
        available_samples = len(df_clean) - min_train_size

        if available_samples < step_size:
            raise ValueError(
                f"No hay suficientes muestras para walk-forward. "
                f"Disponibles: {available_samples}, Step requerido: {step_size}"
            )

        max_folds = available_samples // step_size
        actual_folds = min(n_folds, max_folds)

        for fold_idx in range(actual_folds):
            train_end = min_train_size + fold_idx * step_size
            test_start = train_end
            test_end = test_start + step_size

            train_df = df_clean.iloc[:train_end]
            test_df = df_clean.iloc[test_start:test_end]

            if len(test_df) == 0:
                continue

            model = XGBoostDemandModel(self.config)
            model.fit(train_df, feature_columns, target_col)

            y_test = test_df[target_col].values
            y_pred = model.predict(test_df)

            metrics = calculate_metrics(y_test, y_pred)
            metrics["fold"] = fold_idx
            metrics["train_size"] = len(train_df)
            metrics["test_size"] = len(test_df)

            fold_results.append(metrics)

        if len(fold_results) == 0:
            return {
                "mape_mean": np.nan,
                "mape_std": np.nan,
                "mae_mean": np.nan,
                "mae_std": np.nan,
                "bias_mean": np.nan,
                "n_folds": 0,
                "fold_results": [],
                "cumple_ca01": False,
                "mensaje": "No se pudieron ejecutar folds de validación",
            }

        aggregate_metrics = {
            "mape_mean": np.mean([r["mape"] for r in fold_results]),
            "mape_std": np.std([r["mape"] for r in fold_results]),
            "mae_mean": np.mean([r["mae"] for r in fold_results]),
            "mae_std": np.std([r["mae"] for r in fold_results]),
            "bias_mean": np.mean([r["bias"] for r in fold_results]),
            "n_folds": len(fold_results),
            "fold_results": fold_results,
        }

        cumple_ca01, mensaje = check_acceptance_criteria(
            pd.DataFrame(fold_results),
            target_mape=20.0,
            target_pct_skus=70.0,
        )

        aggregate_metrics["cumple_ca01"] = cumple_ca01
        aggregate_metrics["mensaje"] = mensaje

        return aggregate_metrics

    def evaluate_by_sku_walk_forward(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        group_cols: List[str] = None,
        n_folds: int = 3,
        min_train_size: int = 30,
    ) -> pd.DataFrame:
        """
        Ejecuta walk-forward validation por SKU.
        
        Args:
            df: DataFrame con columnas group_cols, features y target
            feature_columns: Features a usar
            target_col: Columna target
            group_cols: Columnas para agrupar (ej: ["store_nbr", "family"])
            n_folds: Número de folds por SKU
            min_train_size: Mínimo de muestras para train
        
        Returns:
            DataFrame con métricas por SKU
        """
        if group_cols is None:
            group_cols = ["store_nbr", "family"]

        results = []

        for group_values, group_df in df.groupby(group_cols):
            group_df = group_df.sort_values("week_start")

            if len(group_df) < min_train_size + n_folds:
                continue

            try:
                evaluator = WalkForwardEvaluator(self.config)
                metrics = evaluator.evaluate_walk_forward(
                    group_df,
                    feature_columns,
                    target_col,
                    n_folds=n_folds,
                    min_train_size=min_train_size,
                    step_size=1,
                )

                result_row = {col: val for col, val in zip(group_cols, group_values)}
                result_row["mape"] = metrics["mape_mean"]
                result_row["mae"] = metrics["mae_mean"]
                result_row["bias"] = metrics["bias_mean"]
                result_row["n_folds"] = metrics["n_folds"]
                result_row["n_samples"] = len(group_df)

                results.append(result_row)
            except Exception:
                continue

        if len(results) == 0:
            return pd.DataFrame()

        return pd.DataFrame(results)

    def check_model_reliability(
        self,
        metrics_df: pd.DataFrame,
        mape_threshold: Optional[float] = None,
    ) -> Dict[str, any]:
        """
        Evalúa confiabilidad del modelo (RNF-07).
        
        Args:
            metrics_df: DataFrame con métricas por SKU
            mape_threshold: Umbral para baja confianza (default: config.MAPE_LOW_CONFIDENCE_THRESHOLD)
        
        Returns:
            Dict con evaluación de confiabilidad
        """
        mape_threshold = mape_threshold or self.config.MAPE_LOW_CONFIDENCE_THRESHOLD

        if len(metrics_df) == 0:
            return {
                "reliable": False,
                "pct_high_confidence": 0.0,
                "pct_low_confidence": 0.0,
                "n_skus": 0,
                "mensaje": "No hay datos para evaluar",
            }

        pct_high, pct_low = evaluate_confidence_level(metrics_df, mape_threshold)

        reliable = pct_high >= 70.0

        return {
            "reliable": reliable,
            "pct_high_confidence": pct_high,
            "pct_low_confidence": pct_low,
            "n_skus": len(metrics_df),
            "mape_threshold": mape_threshold,
            "mensaje": (
                f"{'MODELO CONFIABLE' if reliable else 'MODELO DE BAJA CONFIANZA'}: "
                f"{pct_high:.1f}% de SKU con alta confianza (MAPE ≤ {mape_threshold}%)"
            ),
        }

    def generate_evaluation_report(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        pilot_families: Optional[List[str]] = None,
    ) -> Dict:
        """
        Genera reporte completo de evaluación.
        
        Args:
            df: DataFrame con datos
            feature_columns: Features a usar
            target_col: Columna target
            pilot_families: Familias piloto a evaluar
        
        Returns:
            Dict con reporte completo
        """
        pilot_families = pilot_families or self.config.PILOT_FAMILIES

        df_pilot = df[df["family"].isin(pilot_families)].copy()

        global_metrics = self.evaluate_walk_forward(
            df_pilot,
            feature_columns,
            target_col,
            n_folds=5,
            min_train_size=50,
        )

        by_sku_metrics = self.evaluate_by_sku_walk_forward(
            df_pilot,
            feature_columns,
            target_col,
            group_cols=["store_nbr", "family"],
            n_folds=3,
            min_train_size=30,
        )

        reliability = self.check_model_reliability(by_sku_metrics)

        cumple_ca01, mensaje_ca01 = check_acceptance_criteria(by_sku_metrics)

        report = {
            "global_metrics": global_metrics,
            "by_sku_metrics": by_sku_metrics,
            "reliability": reliability,
            "cumple_ca01": cumple_ca01,
            "mensaje_ca01": mensaje_ca01,
            "n_pilot_families": len(pilot_families),
            "n_skus_evaluated": len(by_sku_metrics) if len(by_sku_metrics) > 0 else 0,
        }

        return report
