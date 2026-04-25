"""
DEMAND-24 — Predictor (API Pública del Módulo Analítico)

Interface pública para consumo del backend (Lógica de Negocio).
Proporciona métodos de alto nivel para entrenar, predecir y evaluar.

Cumple con:
- Regla I: Separación Estricta (UI es "tonta", Lógica es "ciega")
- Regla VII: Contrato de API como fuente de verdad
- Regla VIII: Zero Tolerance (config desde .env)
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

from .config.ml_config import MLConfig
from .data_adapter.loader import DataLoader
from .data_adapter.aggregator import DataAggregator
from .data_adapter.feature_builder import FeatureBuilder
from .models.xgboost_model import XGBoostDemandModel
from .training.trainer import ModelTrainer
from .training.evaluator import WalkForwardEvaluator
from .models.metrics import check_acceptance_criteria


class DemandPredictor:
    """
    API pública para predicción de demanda.
    
    Ejemplo de uso:
    ```python
    from modulo_analitico.predictor import DemandPredictor
    
    predictor = DemandPredictor()
    predictor.load_data()
    predictor.prepare_data()
    results = predictor.train()
    predictions = predictor.predict(weeks_ahead=4)
    ```
    
    Responsabilidades:
    - Orquestar todo el pipeline de ML
    - Proveer interface simple para el backend
    - Manejar guardado/carga de modelos
    - Generar predicciones con intervalos de confianza
    """

    def __init__(
        self,
        config: Optional[MLConfig] = None,
        model_path: Optional[Path] = None,
    ):
        """
        Inicializa el predictor.
        
        Args:
            config: Configuración de ML (default: carga desde .env)
            model_path: Ruta para guardar/cargar modelo (opcional)
        """
        self.config = config or MLConfig()
        self.model_path = model_path or (self.config.ML_MODELS_DIR / "demand_model")

        self._data_loader = DataLoader(self.config)
        self._aggregator = DataAggregator(self.config)
        self._feature_builder = FeatureBuilder(self.config)
        self._trainer = ModelTrainer(self.config)
        self._evaluator = WalkForwardEvaluator(self.config)

        self._model: Optional[XGBoostDemandModel] = None
        self._train_df: Optional[pd.DataFrame] = None
        self._weekly_df: Optional[pd.DataFrame] = None
        self._features_df: Optional[pd.DataFrame] = None
        self._feature_columns: List[str] = []

        self._metrics: Dict[str, float] = {}
        self._is_ready = False

    def load_data(self) -> "DemandPredictor":
        """
        Carga todos los datos desde CSVs.
        
        Returns:
            self para method chaining
        
        Raises:
            FileNotFoundError: Si los CSVs no existen
            ValueError: Si los datos son inválidos
        """
        print("Cargando datos...")

        train_df, stores_df, holidays_df, oil_df = self._data_loader.load_all_data()

        self._train_df = train_df
        self._stores_df = stores_df
        self._holidays_df = holidays_df
        self._oil_df = oil_df

        valid, mensaje = self._data_loader.validate_minimum_weeks_per_sku(train_df)
        if not valid:
            print(f"ADVERTENCIA: {mensaje}")

        print(f"Datos cargados: {len(train_df):,} filas diarias")
        return self

    def prepare_data(
        self,
        pilot_families: Optional[List[str]] = None,
    ) -> "DemandPredictor":
        """
        Prepara datos: agrega a semanal y construye features.
        
        Args:
            pilot_families: Familias a incluir (default: config.PILOT_FAMILIES)
        
        Returns:
            self para method chaining
        """
        print("Preparando datos...")

        pilot_families = pilot_families or self.config.PILOT_FAMILIES

        train_df = self._train_df.copy()
        train_df = train_df[train_df["family"].isin(pilot_families)]

        weekly_df = self._aggregator.aggregate_daily_to_weekly(
            train_df,
            group_by_family=True,
        )

        features_df = self._feature_builder.build_all_features(
            weekly_df,
            self._stores_df,
            self._holidays_df,
            self._oil_df,
        )

        self._feature_columns = self._feature_builder.get_feature_columns(features_df)

        self._weekly_df = weekly_df
        self._features_df = features_df

        print(f"Datos preparados: {len(features_df):,} filas semanales")
        print(f"   Features: {len(self._feature_columns)} columnas")
        print(f"   Familias piloto: {len(pilot_families)}")

        return self

    def train(
        self,
        use_cross_validation: bool = True,
        save_model: bool = True,
    ) -> Dict[str, float]:
        """
        Entrena el modelo.
        
        Args:
            use_cross_validation: Si True, usa TimeSeriesSplit CV
            save_model: Si True, guarda el modelo en disco
        
        Returns:
            Dict con métricas de entrenamiento
        
        Raises:
            RuntimeError: Si no se han cargado/preparado datos
        """
        if self._features_df is None:
            raise RuntimeError("Datos no preparados. Llamar a load_data() y prepare_data() primero.")

        print("Entrenando modelo...")

        if use_cross_validation:
            self._model, metrics, fold_metrics = self._trainer.train_with_cross_validation(
                self._features_df,
                self._feature_columns,
                "sales",
                n_splits=self.config.N_SPLITS,
            )
            print(f"CV completado: {len(fold_metrics)} folds")
            print(f"   MAPE promedio: {metrics['mape_mean']:.2f}% ± {metrics['mape_std']:.2f}%")
        else:
            self._model, metrics, _ = self._trainer.train(
                self._features_df,
                self._feature_columns,
                "sales",
                test_size=0.2,
            )
            print(f"Train/Test completado")
            print(f"   MAPE: {metrics['mape']:.2f}%")

        self._metrics = metrics

        if save_model:
            self.save_model()
            print(f"Modelo guardado en: {self.model_path}")

        self._is_ready = True

        return metrics

    def predict(
        self,
        weeks_ahead: int = 4,
        with_confidence_intervals: bool = True,
    ) -> pd.DataFrame:
        """
        Genera predicciones para las próximas semanas.
        Implementa RF-03 (Generación de Predicción).
        
        Args:
            weeks_ahead: Número de semanas a predecir (1-4)
            with_confidence_intervals: Si True, incluye CI al 90%
        
        Returns:
            DataFrame con predicciones:
            - week_start, store_nbr, family
            - prediction (demanda estimada)
            - ci_lower, ci_upper (si with_confidence_intervals=True)
            - confidence_level ("HIGH" o "LOW")
        
        Raises:
            RuntimeError: Si el modelo no está entrenado
        """
        if not self._is_ready or self._model is None:
            raise RuntimeError("Modelo no entrenado. Llamar a train() primero.")

        print(f"Generando predicciones para {weeks_ahead} semanas...")

        last_week = self._features_df["week_start"].max()
        last_week = pd.to_datetime(last_week)

        future_weeks = pd.date_range(
            start=last_week + pd.Timedelta(days=7),
            periods=weeks_ahead,
            freq="W-MON",
        )

        predictions = []

        for store_nbr in self._features_df["store_nbr"].unique():
            for family in self._features_df["family"].unique():
                sku_df = self._features_df[
                    (self._features_df["store_nbr"] == store_nbr) &
                    (self._features_df["family"] == family)
                ].copy()

                for week_start in future_weeks:
                    future_row = self._create_future_row(
                        sku_df,
                        store_nbr,
                        family,
                        week_start,
                    )

                    if future_row is None:
                        continue

                    if with_confidence_intervals:
                        pred, ci_lower, ci_upper = self._model.predict_with_confidence_intervals(
                            future_row
                        )
                        row_dict = {
                            "week_start": week_start,
                            "store_nbr": store_nbr,
                            "family": family,
                            "prediction": float(pred[0]),
                            "ci_lower": float(ci_lower[0]),
                            "ci_upper": float(ci_upper[0]),
                        }
                    else:
                        pred = self._model.predict(future_row)
                        row_dict = {
                            "week_start": week_start,
                            "store_nbr": store_nbr,
                            "family": family,
                            "prediction": float(pred[0]),
                        }

                    predictions.append(row_dict)

        predictions_df = pd.DataFrame(predictions)

        if with_confidence_intervals:
            predictions_df["confidence_level"] = predictions_df.apply(
                lambda row: "HIGH" if self._metrics.get("mape_mean", 0) <= self.config.MAPE_LOW_CONFIDENCE_THRESHOLD else "LOW",
                axis=1,
            )

        print(f"Predicciones generadas: {len(predictions_df)} filas")

        return predictions_df

    def _create_future_row(
        self,
        historical_df: pd.DataFrame,
        store_nbr: int,
        family: str,
        week_start: pd.Timestamp,
    ) -> Optional[pd.DataFrame]:
        """
        Crea una fila con features para una semana futura.
        
        Notes:
            - Usa últimos valores conocidos para lags y rolling stats
            - Features temporales se calculan para week_start
            - Holiday features asumen no hay festivos (desconocido)
        """
        if len(historical_df) == 0:
            return None

        last_row = historical_df.iloc[-1:].copy()
        last_row["week_start"] = week_start

        last_row["year"] = week_start.year
        last_row["month"] = week_start.month
        last_row["week_of_year"] = week_start.isocalendar().week
        last_row["day_of_week"] = week_start.dayofweek
        last_row["is_month_start"] = 1 if week_start.day <= 7 else 0
        last_row["is_month_end"] = 1 if week_start.day >= 25 else 0
        last_row["is_quarter_start"] = 1 if week_start.is_quarter_start else 0
        last_row["is_quarter_end"] = 1 if week_start.is_quarter_end else 0
        last_row["days_in_month"] = week_start.daysinmonth

        last_row["is_holiday"] = 0
        last_row["holiday_type"] = 0
        last_row["is_holiday_week_national"] = 0
        last_row["is_holiday_week_regional"] = 0
        last_row["is_holiday_week_local"] = 0

        last_row["onpromotion"] = last_row.get("onpromotion", 0)
        last_row["has_promotion"] = 1 if last_row["onpromotion"] > 0 else 0

        for col in self._feature_columns:
            if col not in last_row.columns:
                if "lag" in col or "rolling" in col:
                    last_row[col] = last_row.get("sales", 0)
                elif "oil" in col:
                    last_row[col] = last_row.get("oil_price", 0)
                else:
                    last_row[col] = 0

        return last_row[self._feature_columns]

    def evaluate(self) -> Dict:
        """
        Evalúa el modelo con walk-forward validation.
        
        Returns:
            Dict con reporte completo de evaluación
        """
        if self._features_df is None:
            raise RuntimeError("Datos no preparados. Llamar a prepare_data() primero.")

        print("Evaluando modelo con walk-forward validation...")

        report = self._evaluator.generate_evaluation_report(
            self._features_df,
            self._feature_columns,
            "sales",
            pilot_families=self.config.PILOT_FAMILIES,
        )

        print(f"   {report['mensaje_ca01']}")
        print(f"   Confiabilidad: {report['reliability']['mensaje']}")

        return report

    def save_model(self, path: Optional[Path] = None) -> None:
        """
        Guarda el modelo en disco.
        
        Args:
            path: Ruta para guardar (default: self.model_path)
        """
        if self._model is None:
            raise RuntimeError("No hay modelo para guardar.")

        path = path or self.model_path
        self._model.save(path, metadata={"train_date": pd.Timestamp.now()})

    def load_model(self, path: Optional[Path] = None) -> "DemandPredictor":
        """
        Carga un modelo desde disco.
        
        Args:
            path: Ruta del modelo (default: self.model_path)
        
        Returns:
            self para method chaining
        """
        path = path or self.model_path

        if not path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {path}")

        self._model = XGBoostDemandModel(self.config)
        self._model.load(path)
        self._metrics = self._model.get_metrics()
        self._is_ready = True

        print(f"Modelo cargado desde: {path}")
        return self

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Retorna importancia de features.
        
        Returns:
            DataFrame con (feature, importance) o None
        """
        if self._model is None:
            return None

        return self._model.get_top_features(n=15)

    def get_metrics(self) -> Dict[str, float]:
        """
        Retorna métricas del modelo.
        
        Returns:
            Dict con métricas
        """
        return self._metrics.copy()

    @property
    def is_ready(self) -> bool:
        """Verifica si el predictor está listo para usar."""
        return self._is_ready

    def save_predictions_to_db(self, predictions_df: pd.DataFrame, db_session) -> int:
        """
        Persiste predicciones en BD usando el Repository Pattern.

        Args:
            predictions_df: DataFrame con columnas:
                sku_id, week_start, predicted_demand, confidence_level,
                lower_bound, upper_bound, mape (todas requeridas).
            db_session: Sesión SQLAlchemy activa.

        Returns:
            Número de predicciones guardadas.

        Raises:
            ValueError: Si las columnas requeridas no existen en el DataFrame.
            RuntimeError: Si la inserción falla.
        """
        # Lazy import para no acoplar módulo analítico a capa de datos
        from logica_negocio.database.repositories import PredictionRepository
        from logica_negocio.database.schemas import PredictionCreate

        required_columns = {
            "sku_id", "week_start", "predicted_demand",
            "confidence_level", "lower_bound", "upper_bound", "mape",
        }
        missing = required_columns - set(predictions_df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes en predictions_df: {missing}")

        repo = PredictionRepository(db_session)

        prediction_dtos = []
        for _, row in predictions_df.iterrows():
            pred_schema = PredictionCreate(
                sku_id=int(row["sku_id"]),
                week_start=row["week_start"],
                predicted_demand=float(row["predicted_demand"]),
                confidence_level=float(row["confidence_level"]),
                lower_bound=float(row["lower_bound"]),
                upper_bound=float(row["upper_bound"]),
                mape=float(row["mape"]),
            )
            prediction_dtos.append(pred_schema)

        try:
            results = repo.bulk_create(prediction_dtos)
            return len(results)
        except Exception as e:
            raise RuntimeError(f"Error guardando predicciones: {e}") from e

    def save_training_results_to_db(
        self,
        model_version: str,
        db_session,
        fold_metrics: Optional[List[Dict]] = None,
    ) -> None:
        """
        Persiste métricas de entrenamiento y versión del modelo en BD.

        Args:
            model_version: String de versión (e.g. 'v1.0.0').
            db_session: Sesión SQLAlchemy activa.
            fold_metrics: Lista de dicts con métricas por fold (opcional).

        Raises:
            RuntimeError: Si no hay métricas disponibles.
        """
        if not self._metrics:
            raise RuntimeError("No hay métricas. Llamar a train() primero.")

        # Lazy imports
        from logica_negocio.database.repositories import (
            EvaluationFoldRepository,
            ModelVersionRepository,
        )
        from logica_negocio.database.schemas import (
            EvaluationFoldCreate,
            ModelVersionCreate,
        )

        # Guardar versión del modelo
        model_repo = ModelVersionRepository(db_session)
        model_data = ModelVersionCreate(
            version=model_version,
            random_seed=self.config.RANDOM_SEED,
            n_splits=self.config.N_SPLITS,
            xgboost_params={
                "max_depth": self.config.XGBOOST_MAX_DEPTH,
                "learning_rate": self.config.XGBOOST_LEARNING_RATE,
                "n_estimators": self.config.XGBOOST_N_ESTIMATORS,
                "subsample": self.config.XGBOOST_SUBSAMPLE,
                "colsample_bytree": self.config.XGBOOST_COLSAMPLE_BYTREE,
            },
            acceptance_criteria_met=self._metrics.get("acceptance_criteria_met"),
        )
        model_repo.create(model_data)

        # Guardar fold metrics si hay
        if fold_metrics:
            eval_repo = EvaluationFoldRepository(db_session)
            eval_dtos = [
                EvaluationFoldCreate(
                    fold_number=fm.get("fold_number", idx + 1),
                    sku_id=fm.get("sku_id"),
                    mape=fm.get("mape"),
                    mae=fm.get("mae"),
                    bias=fm.get("bias"),
                )
                for idx, fm in enumerate(fold_metrics)
            ]
            eval_repo.bulk_create(eval_dtos)


def main():
    """
    Script de ejemplo para probar el pipeline completo.
    """
    print("=" * 60)
    print("DEMAND-24 — Pipeline de Predicción de Demanda")
    print("=" * 60)

    predictor = DemandPredictor()

    try:
        predictor.load_data()
        predictor.prepare_data()

        metrics = predictor.train(use_cross_validation=True)

        print("\n" + "=" * 60)
        print("MÉTRICAS DE ENTRENAMIENTO")
        print("=" * 60)
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

        report = predictor.evaluate()

        print("\n" + "=" * 60)
        print("EVALUACIÓN")
        print("=" * 60)
        print(f"Cumple CA-01: {report['cumple_ca01']}")
        print(f"SKU evaluados: {report['n_skus_evaluated']}")

        predictions = predictor.predict(weeks_ahead=4, with_confidence_intervals=True)

        print("\n" + "=" * 60)
        print("PREDICCIONES (primeras 10 filas)")
        print("=" * 60)
        print(predictions.head(10).to_string())

        print("\nPipeline completado exitosamente!")

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nAsegúrate de descargar los datasets desde:")
        print("https://www.kaggle.com/competitions/store-sales-time-series-forecasting")
        print("Y colocarlos en: data/raw/")

    except Exception as e:
        print(f"\nERROR inesperado: {e}")
        raise


if __name__ == "__main__":
    main()
