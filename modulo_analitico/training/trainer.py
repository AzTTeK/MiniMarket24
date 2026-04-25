"""
DEMAND-24 — Entrenamiento de Modelos

Responsable del entrenamiento del modelo XGBoost con validación temporal.

Cumple con:
- Regla VI: Anti-Leakage (TimeSeriesSplit)
- Regla VI: Reproducibilidad (random_seed desde config)
- Regla I: Separación de Responsabilidades
"""

from typing import Tuple, Dict, Optional, List
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import TimeSeriesSplit

from ..config.ml_config import MLConfig
from ..models.xgboost_model import XGBoostDemandModel
from ..models.metrics import calculate_metrics, calculate_metrics_by_sku


class ModelTrainer:
    """
    Entrena modelos de predicción de demanda.
    
    Responsabilidades:
    - Dividir datos con TimeSeriesSplit (anti-leakage)
    - Entrenar modelo XGBoost
    - Evaluar con métricas (MAPE, MAE, Bias)
    - Versionar modelos
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()

    def train(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        test_size: float = 0.2,
    ) -> Tuple[XGBoostDemandModel, Dict[str, float], pd.DataFrame]:
        """
        Entrena un modelo con split temporal.
        
        Args:
            df: DataFrame con features y target
            feature_columns: Columnas a usar como features
            target_col: Columna target
            test_size: Porcentaje de datos para test (últimos períodos)
        
        Returns:
            Tuple con (modelo_entrenado, métricas, DataFrame predicciones)
        
        Notes:
            - Usa split temporal (últimos períodos para test)
            - NO shuffle para evitar data leakage
        """
        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=feature_columns + [target_col])

        if len(df_clean) == 0:
            raise ValueError("No hay datos válidos para entrenar después de eliminar NaN.")

        split_idx = int(len(df_clean) * (1 - test_size))

        train_df = df_clean.iloc[:split_idx]
        test_df = df_clean.iloc[split_idx:]

        if len(train_df) < 10:
            raise ValueError(
                f"Datos de entrenamiento insuficientes: {len(train_df)} filas. "
                f"Se requieren al menos 10 filas."
            )

        if len(test_df) < 5:
            raise ValueError(
                f"Datos de test insuficientes: {len(test_df)} filas. "
                f"Se requieren al menos 5 filas."
            )

        model = XGBoostDemandModel(self.config)
        model.fit(train_df, feature_columns, target_col)

        X_test = test_df[feature_columns].values
        y_test = test_df[target_col].values

        y_pred = model.predict(test_df)

        test_df = test_df.copy()
        test_df["prediction"] = y_pred

        metrics = calculate_metrics(y_test, y_pred)
        metrics["n_train"] = len(train_df)
        metrics["n_test"] = len(test_df)

        model.set_metrics(metrics)

        return model, metrics, test_df

    def train_with_cross_validation(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        n_splits: Optional[int] = None,
    ) -> Tuple[XGBoostDemandModel, Dict[str, float], List[Dict]]:
        """
        Entrena con TimeSeriesSplit cross-validation.
        Implementa Regla VI: Anti-Leakage.
        
        Args:
            df: DataFrame con features y target
            feature_columns: Columnas a usar como features
            target_col: Columna target
            n_splits: Número de folds (default: config.N_SPLITS)
        
        Returns:
            Tuple con (modelo_final, métricas_promedio, lista_métricas_por_fold)
        
        Notes:
            - TimeSeriesSplit garantiza que test siempre es después de train
            - Modelo final se entrena con todos los datos
        """
        n_splits = n_splits or self.config.N_SPLITS

        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=feature_columns + [target_col])

        if len(df_clean) < n_splits * 10:
            raise ValueError(
                f"Datos insuficientes para {n_splits} folds. "
                f"Se requieren al menos {n_splits * 10} filas, hay {len(df_clean)}."
            )

        tscv = TimeSeriesSplit(n_splits=n_splits)

        fold_metrics = []

        for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(df_clean)):
            train_fold = df_clean.iloc[train_idx]
            test_fold = df_clean.iloc[test_idx]

            model_fold = XGBoostDemandModel(self.config)
            model_fold.fit(train_fold, feature_columns, target_col)

            y_test = test_fold[target_col].values
            y_pred = model_fold.predict(test_fold)

            metrics = calculate_metrics(y_test, y_pred)
            metrics["fold"] = fold_idx
            metrics["n_train"] = len(train_fold)
            metrics["n_test"] = len(test_fold)

            fold_metrics.append(metrics)

        avg_metrics = {
            "mape_mean": np.mean([m["mape"] for m in fold_metrics]),
            "mape_std": np.std([m["mape"] for m in fold_metrics]),
            "mae_mean": np.mean([m["mae"] for m in fold_metrics]),
            "mae_std": np.std([m["mae"] for m in fold_metrics]),
            "bias_mean": np.mean([m["bias"] for m in fold_metrics]),
            "n_folds": n_splits,
        }

        model_final = XGBoostDemandModel(self.config)
        model_final.fit(df_clean, feature_columns, target_col)
        model_final.set_metrics(avg_metrics)

        return model_final, avg_metrics, fold_metrics

    def train_by_family(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        pilot_families: Optional[List[str]] = None,
    ) -> Dict[str, Tuple[XGBoostDemandModel, Dict[str, float]]]:
        """
        Entrena un modelo por familia de productos.
        
        Args:
            df: DataFrame con columnas family, features y target
            feature_columns: Columnas a usar como features
            target_col: Columna target
            pilot_families: Lista de familias piloto (default: config.PILOT_FAMILIES)
        
        Returns:
            Dict con {family: (modelo, métricas)}
        """
        pilot_families = pilot_families or self.config.PILOT_FAMILIES

        results = {}

        for family in pilot_families:
            family_df = df[df["family"] == family].copy()

            if len(family_df) < 50:
                print(f"WARNING: Familia {family}: solo {len(family_df)} filas, se salta.")
                continue

            try:
                model, metrics, _ = self.train(
                    family_df,
                    feature_columns,
                    target_col,
                    test_size=0.2,
                )
                results[family] = (model, metrics)
                print(f"SUCCESS: Familia {family}: MAPE={metrics['mape']:.2f}%")
            except Exception as e:
                print(f"ERROR: Familia {family}: Error - {str(e)}")

        return results

    def validate_minimum_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
        min_samples: int = 50,
    ) -> Tuple[bool, str]:
        """
        Valida que hay datos suficientes para entrenar.
        
        Args:
            df: DataFrame con datos
            feature_columns: Features a usar
            target_col: Columna target
            min_samples: Mínimo de muestras requeridas
        
        Returns:
            Tuple con (es_valido, mensaje)
        """
        df_clean = df.dropna(subset=feature_columns + [target_col])

        if len(df_clean) < min_samples:
            return False, (
                f"Datos insuficientes: {len(df_clean)} filas después de eliminar NaN. "
                f"Se requieren al menos {min_samples}."
            )

        null_counts = df_clean[feature_columns + [target_col]].isnull().sum()
        if null_counts.any():
            return False, f"Columnas con nulos: {null_counts[null_counts > 0].to_dict()}"

        return True, f"Datos válidos: {len(df_clean)} filas"
