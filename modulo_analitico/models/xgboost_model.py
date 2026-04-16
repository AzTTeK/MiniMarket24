"""
DEMAND-24 — Modelo XGBoost

Implementación del modelo predictivo principal usando XGBoost.

Cumple con:
- Regla I: Agnosticismo (usa XGBoostModelWrapper)
- Regla VI: Reproducibilidad (random_seed desde config)
- Regla VIII: Zero Tolerance (nada hardcodeado)
"""

from pathlib import Path
from typing import Tuple, Optional, Dict, List
import numpy as np
import pandas as pd
import joblib

from ..config.ml_config import MLConfig
from ..wrappers.xgboost_wrapper import XGBoostModelWrapper


class XGBoostDemandModel:
    """
    Modelo de predicción de demanda usando XGBoost.
    
    Responsabilidades:
    - Entrenar modelo por SKU o familia
    - Generar predicciones con intervalos de confianza
    - Guardar/cargar modelos versionados
    - Calcular feature importance
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()
        self._model: Optional[XGBoostModelWrapper] = None
        self._feature_columns: List[str] = []
        self._is_fitted = False
        self._metrics: Dict[str, float] = {}

    def fit(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_col: str = "sales",
    ) -> "XGBoostDemandModel":
        """
        Entrena el modelo XGBoost.
        
        Args:
            df: DataFrame con features y target
            feature_columns: Lista de columnas a usar como features
            target_col: Columna target (default: "sales")
        
        Returns:
            self para method chaining
        
        Notes:
            - Elimina filas con NaN antes de entrenar
            - Usa random_seed desde config para reproducibilidad
        """
        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=feature_columns + [target_col])

        if len(df_clean) == 0:
            raise ValueError(
                "No hay datos válidos para entrenar. "
                "Verificar que el DataFrame tenga datos después de eliminar NaN."
            )

        X = df_clean[feature_columns].values
        y = df_clean[target_col].values

        self._model = XGBoostModelWrapper(
            max_depth=self.config.XGBOOST_MAX_DEPTH,
            learning_rate=self.config.XGBOOST_LEARNING_RATE,
            n_estimators=self.config.XGBOOST_N_ESTIMATORS,
            subsample=self.config.XGBOOST_SUBSAMPLE,
            colsample_bytree=self.config.XGBOOST_COLSAMPLE_BYTREE,
            random_state=self.config.RANDOM_SEED,
        )

        self._model.fit(X, y)
        self._feature_columns = feature_columns.copy()
        self._is_fitted = True

        return self

    def predict(
        self,
        df: pd.DataFrame,
    ) -> np.ndarray:
        """
        Genera predicciones puntuales.
        
        Args:
            df: DataFrame con features
        
        Returns:
            Array con predicciones
        """
        if not self._is_fitted or self._model is None:
            raise RuntimeError("El modelo no ha sido entrenado. Llamar a fit() primero.")

        X = df[self._feature_columns].values
        predictions = self._model.predict(X)

        return predictions

    def predict_with_confidence_intervals(
        self,
        df: pd.DataFrame,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Genera predicciones con intervalos de confianza al 90%.
        Implementa RF-03 (Generación de Predicción con CI).
        
        Args:
            df: DataFrame con features
        
        Returns:
            Tuple con (predicción_media, límite_inferior, límite_superior)
        """
        if not self._is_fitted or self._model is None:
            raise RuntimeError("El modelo no ha sido entrenado. Llamar a fit() primero.")

        X = df[self._feature_columns].values

        pred_median, pred_lower, pred_upper = self._model.predict_with_quantiles(
            X,
            lower_quantile=self.config.LOWER_QUANTILE,
            upper_quantile=self.config.UPPER_QUANTILE,
        )

        return pred_median, pred_lower, pred_upper

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Retorna importancia de features.
        
        Returns:
            Dict con {feature: importance} o None si no entrenado
        """
        if not self._is_fitted or self._model is None:
            return None

        importances = self._model.feature_importances()

        if importances is None:
            return None

        return dict(zip(self._feature_columns, importances))

    def get_top_features(self, n: int = 10) -> Optional[pd.DataFrame]:
        """
        Retorna las top N features por importancia.
        
        Args:
            n: Número de features a retornar
        
        Returns:
            DataFrame con (feature, importance) ordenado
        """
        importance_dict = self.get_feature_importance()

        if importance_dict is None:
            return None

        importance_df = pd.DataFrame(
            list(importance_dict.items()),
            columns=["feature", "importance"],
        )
        importance_df = importance_df.sort_values("importance", ascending=False)

        return importance_df.head(n)

    def save(
        self,
        path: Path,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Guarda el modelo y metadata en disco.
        
        Args:
            path: Ruta base para guardar (sin extensión)
            metadata: Dict adicional para guardar (ej: métricas, fecha)
        
        Notes:
            - Guarda modelo como .json (formato XGBoost)
            - Guarda metadata como .pkl (joblib)
        """
        if not self._is_fitted or self._model is None:
            raise RuntimeError("No se puede guardar un modelo no entrenado.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        model_path = path.with_suffix(".json")
        metadata_path = path.with_suffix(".pkl")

        self._model.save(model_path)

        metadata_to_save = {
            "feature_columns": self._feature_columns,
            "metrics": self._metrics,
            "config": {
                "RANDOM_SEED": self.config.RANDOM_SEED,
                "XGBOOST_MAX_DEPTH": self.config.XGBOOST_MAX_DEPTH,
                "XGBOOST_LEARNING_RATE": self.config.XGBOOST_LEARNING_RATE,
                "XGBOOST_N_ESTIMATORS": self.config.XGBOOST_N_ESTIMATORS,
            },
        }
        if metadata:
            metadata_to_save.update(metadata)

        joblib.dump(metadata_to_save, metadata_path)

    def load(self, path: Path) -> "XGBoostDemandModel":
        """
        Carga un modelo desde disco.
        
        Args:
            path: Ruta base del modelo (sin extensión)
        
        Returns:
            self para method chaining
        """
        path = Path(path)

        model_path = path.with_suffix(".json")
        metadata_path = path.with_suffix(".pkl")

        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")

        self._model = XGBoostModelWrapper(
            max_depth=self.config.XGBOOST_MAX_DEPTH,
            learning_rate=self.config.XGBOOST_LEARNING_RATE,
            n_estimators=self.config.XGBOOST_N_ESTIMATORS,
            subsample=self.config.XGBOOST_SUBSAMPLE,
            colsample_bytree=self.config.XGBOOST_COLSAMPLE_BYTREE,
            random_state=self.config.RANDOM_SEED,
        )
        self._model.load(model_path)

        if metadata_path.exists():
            metadata = joblib.load(metadata_path)
            self._feature_columns = metadata.get("feature_columns", [])
            self._metrics = metadata.get("metrics", {})

        self._is_fitted = True

        return self

    def set_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Establece las métricas de evaluación del modelo.
        
        Args:
            metrics: Dict con métricas (mape, mae, bias, etc.)
        """
        self._metrics = metrics

    def get_metrics(self) -> Dict[str, float]:
        """
        Retorna las métricas de evaluación.
        
        Returns:
            Dict con métricas
        """
        return self._metrics.copy()

    @property
    def is_fitted(self) -> bool:
        """Verifica si el modelo está entrenado."""
        return self._is_fitted
