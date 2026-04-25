"""
DEMAND-24 — Tests para ModelTrainer
"""

import pytest
import pandas as pd
import numpy as np
from modulo_analitico.training.trainer import ModelTrainer
from modulo_analitico.config.ml_config import MLConfig


@pytest.fixture
def sample_df():
    """DataFrame mínimo para tests."""
    np.random.seed(42)
    n_rows = 100
    return pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=n_rows, freq="D"),
        "store_nbr": 1,
        "family": "GROCERY I",
        "sales": np.random.randint(10, 100, n_rows),
        "onpromotion": np.random.randint(0, 5, n_rows),
    })


@pytest.fixture
def features_df(sample_df):
    """DataFrame con features ya calculadas."""
    df = sample_df.copy()
    df["week_start"] = df["date"].dt.to_period("W-SUN").dt.start_time
    df["lag_1"] = df["sales"].shift(1)
    df["lag_2"] = df["sales"].shift(2)
    df["rolling_mean_7"] = df["sales"].rolling(7).mean()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df = df.dropna()
    return df


class TestModelTrainerTrain:
    """Tests para train()."""

    def test_train_success(self, features_df):
        """Entrenamiento básico funciona."""
        trainer = ModelTrainer()
        feature_cols = ["lag_1", "lag_2", "rolling_mean_7"]
        
        model, metrics, test_df = trainer.train(
            features_df, feature_cols, "sales", test_size=0.2
        )
        
        assert model is not None
        assert "mape" in metrics
        assert "mae" in metrics
        assert len(test_df) > 0
        assert "prediction" in test_df.columns

    def test_train_insufficient_train_data(self, features_df):
        """Lanza error si hay pocos datos para train."""
        trainer = ModelTrainer()
        small_df = features_df.head(12)
        
        with pytest.raises(ValueError, match="entrenamiento insuficientes"):
            trainer.train(small_df, ["lag_1"], "sales", test_size=0.5)

    def test_train_insufficient_test_data(self, features_df):
        """Lanza error si hay pocos datos para test."""
        trainer = ModelTrainer()
        small_df = features_df.head(12)
        
        with pytest.raises(ValueError, match="test insuficientes"):
            trainer.train(small_df, ["lag_1"], "sales", test_size=0.1)

    def test_train_with_nan(self, features_df):
        """Elimina NaN antes de entrenar."""
        trainer = ModelTrainer()
        df_with_nan = features_df.copy()
        df_with_nan.loc[0:5, "lag_1"] = np.nan
        
        feature_cols = ["lag_1", "lag_2"]
        model, metrics, test_df = trainer.train(
            df_with_nan, feature_cols, "sales", test_size=0.2
        )
        
        assert model is not None
        assert metrics["mape"] >= 0


class TestModelTrainerCrossValidation:
    """Tests para train_with_cross_validation()."""

    def test_cv_success(self, features_df):
        """CV con TimeSeriesSplit funciona."""
        trainer = ModelTrainer()
        feature_cols = ["lag_1", "lag_2", "rolling_mean_7"]
        
        model, metrics, fold_metrics = trainer.train_with_cross_validation(
            features_df, feature_cols, "sales", n_splits=3
        )
        
        assert model is not None
        assert "mape_mean" in metrics
        assert "mape_std" in metrics
        assert len(fold_metrics) == 3
        assert all("fold" in m for m in fold_metrics)

    def test_cv_insufficient_folds(self, features_df):
        """Lanza error si no hay datos para todos los folds."""
        trainer = ModelTrainer()
        small_df = features_df.head(20)
        
        with pytest.raises(ValueError, match="Datos insuficientes"):
            trainer.train_with_cross_validation(
                small_df, ["lag_1"], "sales", n_splits=5
            )


class TestModelTrainerByFamily:
    """Tests para train_by_family()."""

    def test_train_by_family_success(self, sample_df):
        """Entrena por familia funciona."""
        trainer = ModelTrainer()
        
        # Crear features simples
        df = sample_df.copy()
        df["lag_1"] = df["sales"].shift(1)
        df = df.dropna()
        
        results = trainer.train_by_family(
            df, ["lag_1"], "sales", pilot_families=["GROCERY I"]
        )
        
        assert "GROCERY I" in results
        model, metrics = results["GROCERY I"]
        assert model is not None
        assert "mape" in metrics

    def test_train_by_family_skip_small(self, sample_df):
        """Salta familias con pocos datos."""
        trainer = ModelTrainer()
        
        # Filtrar para tener pocos datos
        small_df = sample_df[sample_df["family"] == "GROCERY I"].head(30)
        
        results = trainer.train_by_family(
            small_df, ["lag_1"], "sales", pilot_families=["GROCERY I"]
        )
        
        assert "GROCERY I" not in results  # Se saltó por tener <50 rows

    def test_train_by_family_custom_families(self, sample_df):
        """Usa lista personalizada de familias."""
        trainer = ModelTrainer()
        
        df = sample_df.copy()
        df["lag_1"] = df["sales"].shift(1)
        df = df.dropna()
        
        results = trainer.train_by_family(
            df, ["lag_1"], "sales", pilot_families=["GROCERY I"]
        )
        
        assert len(results) <= 1


class TestModelTrainerValidate:
    """Tests para validate_minimum_data()."""

    def test_validate_success(self, features_df):
        """Validación exitosa con datos suficientes."""
        trainer = ModelTrainer()
        
        is_valid, message = trainer.validate_minimum_data(
            features_df, ["lag_1", "lag_2"], "sales", min_samples=50
        )
        
        assert is_valid is True
        assert "válidos" in message

    def test_validate_insufficient_samples(self, features_df):
        """Falla cuando hay pocos datos."""
        trainer = ModelTrainer()
        small_df = features_df.head(10)
        
        is_valid, message = trainer.validate_minimum_data(
            small_df, ["lag_1"], "sales", min_samples=50
        )
        
        assert is_valid is False
        assert "insuficientes" in message.lower()

    def test_validate_null_columns(self, features_df):
        """Detecta columnas con nulos."""
        trainer = ModelTrainer()
        df_with_nulls = features_df.copy()
        df_with_nulls["lag_1"] = np.nan
        
        is_valid, message = trainer.validate_minimum_data(
            df_with_nulls, ["lag_1"], "sales", min_samples=10
        )
        
        assert is_valid is False
        assert "insuficientes" in message.lower() or "nulos" in message.lower()
