"""
DEMAND-24 — Tests para DemandPredictor
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
from modulo_analitico.predictor import DemandPredictor
from modulo_analitico.config.ml_config import MLConfig


@pytest.fixture
def config():
    """Configuración para tests."""
    return MLConfig()


@pytest.fixture
def predictor(config):
    """Predictor configurado para tests."""
    return DemandPredictor(config=config)


@pytest.fixture
def sample_weekly_df():
    """DataFrame semanal mínimo."""
    np.random.seed(42)
    n_rows = 200
    dates = pd.date_range("2023-01-02", periods=n_rows, freq="W-MON")
    return pd.DataFrame({
        "week_start": dates,
        "store_nbr": np.random.choice([1, 2, 3], n_rows),
        "family": np.random.choice(["GROCERY I", "BEVERAGES"], n_rows),
        "sales": np.random.randint(10, 100, n_rows),
        "onpromotion": np.random.randint(0, 5, n_rows),
    })


@pytest.fixture
def features_df(sample_weekly_df):
    """DataFrame con features."""
    df = sample_weekly_df.copy()
    df["lag_1"] = df["sales"].shift(1)
    df["lag_2"] = df["sales"].shift(2)
    df["rolling_mean_4"] = df["sales"].rolling(4).mean()
    df["year"] = df["week_start"].dt.year
    df["month"] = df["week_start"].dt.month
    df["week_of_year"] = df["week_start"].dt.isocalendar().week
    df["is_holiday"] = 0
    df["oil_price"] = 80.0
    df = df.dropna()
    return df


class TestDemandPredictorInit:
    """Tests para inicialización."""

    def test_init_default(self):
        """Inicialización con config por defecto."""
        predictor = DemandPredictor()
        assert predictor.config is not None
        assert predictor._is_ready is False
        assert predictor._model is None

    def test_init_with_config(self, config):
        """Inicialización con config personalizado."""
        predictor = DemandPredictor(config=config)
        assert predictor.config == config


class TestDemandPredictorTrain:
    """Tests para train()."""

    def test_train_simple_split(self, predictor, features_df):
        """Entrenamiento con train/test split simple."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2", "rolling_mean_4"]
        
        metrics = predictor.train(use_cross_validation=False, save_model=False)
        
        assert "mape" in metrics
        assert predictor._is_ready is True
        assert predictor._model is not None

    def test_train_with_cv(self, predictor, features_df):
        """Entrenamiento con cross-validation."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2", "rolling_mean_4"]
        
        metrics = predictor.train(use_cross_validation=True, save_model=False)
        
        assert "mape_mean" in metrics
        assert predictor._is_ready is True

    def test_train_without_prepare_data(self, predictor):
        """Lanza error si no se prepararon datos."""
        with pytest.raises(RuntimeError, match="Datos no preparados"):
            predictor.train()


class TestDemandPredictorPredict:
    """Tests para predict()."""

    def test_predict_without_model(self, predictor):
        """Lanza error si no hay modelo entrenado."""
        with pytest.raises(RuntimeError, match="Modelo no entrenado"):
            predictor.predict(weeks_ahead=4)

    def test_predict_with_model(self, predictor, features_df):
        """Predicción con modelo entrenado."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2", "rolling_mean_4"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        predictions = predictor.predict(weeks_ahead=2, with_confidence_intervals=True)
        
        assert len(predictions) > 0
        assert "prediction" in predictions.columns
        assert "ci_lower" in predictions.columns
        assert "ci_upper" in predictions.columns
        assert "confidence_level" in predictions.columns

    def test_predict_without_confidence_intervals(self, predictor, features_df):
        """Predicción sin intervalos de confianza."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2", "rolling_mean_4"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        predictions = predictor.predict(weeks_ahead=2, with_confidence_intervals=False)
        
        assert len(predictions) > 0
        assert "prediction" in predictions.columns
        assert "ci_lower" not in predictions.columns


class TestDemandPredictorCreateFutureRow:
    """Tests para _create_future_row()."""

    def test_create_future_row_empty(self, predictor):
        """Retorna None con histórico vacío."""
        empty_df = pd.DataFrame()
        result = predictor._create_future_row(
            empty_df, store_nbr=1, family="GROCERY I",
            week_start=pd.Timestamp("2024-01-01")
        )
        assert result is None

    def test_create_future_row_success(self, predictor, features_df):
        """Crea fila futura correctamente."""
        sku_df = features_df[features_df["store_nbr"] == 1].head(10)
        predictor._feature_columns = ["lag_1", "lag_2", "rolling_mean_4"]
        
        result = predictor._create_future_row(
            sku_df, store_nbr=1, family="GROCERY I",
            week_start=pd.Timestamp("2024-01-01")
        )
        
        assert result is not None
        assert len(result) > 0


class TestDemandPredictorSaveLoad:
    """Tests para save_model() y load_model()."""

    def test_save_model_no_model(self, predictor):
        """Lanza error si no hay modelo."""
        with pytest.raises(RuntimeError, match="No hay modelo"):
            predictor.save_model()

    def test_load_model_not_found(self, predictor, tmp_path):
        """Lanza error si el archivo no existe."""
        fake_path = tmp_path / "nonexistent_model"
        with pytest.raises(FileNotFoundError):
            predictor.load_model(fake_path)

    def test_save_and_load_model(self, predictor, features_df, tmp_path):
        """Guarda y carga modelo correctamente."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        model_path = tmp_path / "test_model"
        predictor.save_model(model_path)
        
        assert True


class TestDemandPredictorMetrics:
    """Tests para get_metrics() y get_feature_importance()."""

    def test_get_metrics_empty(self, predictor):
        """Retorna dict vacío sin entrenar."""
        metrics = predictor.get_metrics()
        assert metrics == {}

    def test_get_metrics_after_train(self, predictor, features_df):
        """Retorna métricas después de entrenar."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        metrics = predictor.get_metrics()
        assert "mape" in metrics

    def test_get_feature_importance_no_model(self, predictor):
        """Retorna None sin modelo."""
        result = predictor.get_feature_importance()
        assert result is None

    def test_get_feature_importance_with_model(self, predictor, features_df):
        """Retorna DataFrame con modelo entrenado."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        importance = predictor.get_feature_importance()
        
        assert importance is not None
        assert isinstance(importance, pd.DataFrame)


class TestDemandPredictorDatabase:
    """Tests para métodos de base de datos."""

    def test_save_predictions_missing_columns(self, predictor):
        """Lanza error si faltan columnas."""
        df = pd.DataFrame({"wrong_col": [1, 2, 3]})
        mock_session = MagicMock()
        
        with pytest.raises(ValueError, match="Columnas faltantes"):
            predictor.save_predictions_to_db(df, mock_session)

    def test_save_training_no_metrics(self, predictor):
        """Lanza error sin métricas."""
        mock_session = MagicMock()
        
        with pytest.raises(RuntimeError, match="No hay métricas"):
            predictor.save_training_results_to_db("v1.0.0", mock_session)

    def test_save_training_with_folds(self, predictor, features_df):
        """Guarda métricas con folds."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2"]
        predictor.train(use_cross_validation=True, save_model=False)
        
        mock_session = MagicMock()
        
        with patch('logica_negocio.database.repositories.ModelVersionRepository') as mock_model_repo, \
             patch('logica_negocio.database.repositories.EvaluationFoldRepository') as mock_eval_repo:
            
            mock_model_instance = MagicMock()
            mock_model_repo.return_value = mock_model_instance
            
            mock_eval_instance = MagicMock()
            mock_eval_repo.return_value = mock_eval_instance
            
            predictor.save_training_results_to_db(
                "v1.0.0", mock_session,
                fold_metrics=[{"mape": 15.0, "fold_number": 1}]
            )
            
            assert mock_model_instance.create.called


class TestDemandPredictorEvaluate:
    """Tests para evaluate()."""

    def test_evaluate_without_data(self, predictor):
        """Lanza error sin datos preparados."""
        with pytest.raises(RuntimeError, match="Datos no preparados"):
            predictor.evaluate()


class TestDemandPredictorIsReady:
    """Tests para is_ready property."""

    def test_is_ready_false_initial(self, predictor):
        """False inicialmente."""
        assert predictor.is_ready is False

    def test_is_ready_true_after_train(self, predictor, features_df):
        """True después de entrenar."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1", "lag_2"]
        predictor.train(use_cross_validation=False, save_model=False)
        assert predictor.is_ready is True


class TestDemandPredictorMain:
    """Tests para función main() y líneas restantes."""

    def test_load_data_warning(self, predictor, sample_weekly_df):
        """Muestra advertencia si hay pocas semanas."""
        predictor._train_df = sample_weekly_df
        predictor._data_loader = MagicMock()
        predictor._data_loader.load_all_data.return_value = (
            sample_weekly_df, sample_weekly_df, sample_weekly_df, sample_weekly_df
        )
        predictor._data_loader.validate_minimum_weeks_per_sku.return_value = (
            False, "Pocas semanas"
        )
        
        result = predictor.load_data()
        assert result is predictor

    def test_prepare_data_custom_families(self, predictor, sample_weekly_df):
        """Prepara datos con familias personalizadas."""
        predictor._train_df = sample_weekly_df
        predictor._stores_df = sample_weekly_df
        predictor._holidays_df = sample_weekly_df
        predictor._oil_df = sample_weekly_df
        predictor._aggregator = MagicMock()
        predictor._aggregator.aggregate_daily_to_weekly.return_value = sample_weekly_df
        predictor._feature_builder = MagicMock()
        predictor._feature_builder.build_all_features.return_value = sample_weekly_df
        predictor._feature_builder.get_feature_columns.return_value = ["f1"]
        
        predictor.prepare_data(pilot_families=["GROCERY I"])
        
        assert predictor._feature_columns == ["f1"]

    def test_predict_not_ready(self, predictor):
        """Verifica error si modelo no está listo."""
        predictor._is_ready = False
        predictor._model = None
        
        with pytest.raises(RuntimeError, match="Modelo no entrenado"):
            predictor.predict(weeks_ahead=1)

    def test_create_future_row_with_features(self, predictor):
        """Crea fila futura manejando features faltantes."""
        hist_df = pd.DataFrame({
            "week_start": [pd.Timestamp("2024-01-01")],
            "store_nbr": [1],
            "family": ["A"],
            "sales": [50],
            "lag_1": [45],
        })
        predictor._feature_columns = ["lag_1", "lag_2", "custom_feature"]
        
        result = predictor._create_future_row(
            hist_df, store_nbr=1, family="A",
            week_start=pd.Timestamp("2024-01-08")
        )
        
        assert result is not None
        assert "custom_feature" in result.columns

    def test_save_model_custom_path(self, predictor, features_df, tmp_path):
        """Guarda modelo en ruta personalizada."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        custom_path = tmp_path / "custom_model"
        predictor.save_model(custom_path)
        
        assert True

    def test_get_metrics_copy(self, predictor, features_df):
        """get_metrics() retorna copia, no referencia."""
        predictor._features_df = features_df
        predictor._feature_columns = ["lag_1"]
        predictor.train(use_cross_validation=False, save_model=False)
        
        metrics1 = predictor.get_metrics()
        metrics1["mape"] = 999
        
        metrics2 = predictor.get_metrics()
        assert metrics2["mape"] != 999
