"""
DEMAND-24 — Tests extendidos para DataAggregator
"""

import pytest
import pandas as pd
import numpy as np
from modulo_analitico.data_adapter.aggregator import DataAggregator
from modulo_analitico.config.ml_config import MLConfig


@pytest.fixture
def daily_df():
    """DataFrame diario para tests."""
    np.random.seed(42)
    n_rows = 100
    dates = pd.date_range("2023-01-01", periods=n_rows, freq="D")
    return pd.DataFrame({
        "date": dates,
        "store_nbr": np.random.choice([1, 2], n_rows),
        "family": np.random.choice(["GROCERY I", "BEVERAGES"], n_rows),
        "sales": np.random.randint(10, 100, n_rows),
        "onpromotion": np.random.randint(0, 5, n_rows),
    })


@pytest.fixture
def weekly_df(daily_df):
    """DataFrame semanal base."""
    agg = DataAggregator()
    return agg.aggregate_daily_to_weekly(daily_df, group_by_family=True)


class TestDataAggregatorCalculateStats:
    """Tests para calculate_weekly_stats()."""

    def test_calculate_weekly_stats_with_family(self, daily_df):
        """Calcula stats agrupando por familia."""
        agg = DataAggregator()
        
        stats = agg.calculate_weekly_stats(daily_df, group_by_family=True)
        
        assert "sales_mean" in stats.columns
        assert "sales_std" in stats.columns
        assert "sales_min" in stats.columns
        assert "sales_max" in stats.columns
        assert "onpromotion_days" in stats.columns
        assert "onpromotion_mean" in stats.columns
        assert "family" in stats.columns

    def test_calculate_weekly_stats_without_family(self, daily_df):
        """Calcula stats sin agrupar por familia."""
        agg = DataAggregator()
        
        stats = agg.calculate_weekly_stats(daily_df, group_by_family=False)
        
        assert "sales_mean" in stats.columns
        assert "family" not in stats.columns


class TestDataAggregatorWeekBoundaries:
    """Tests para get_week_boundaries()."""

    def test_get_week_boundaries(self, daily_df):
        """Obtiene límites de semanas correctamente."""
        agg = DataAggregator()
        
        first, last = agg.get_week_boundaries(daily_df)
        
        assert isinstance(first, pd.Timestamp)
        assert isinstance(last, pd.Timestamp)
        assert first <= last
        assert first.dayofweek == 0  # Lunes


class TestDataAggregatorCompleteIndex:
    """Tests para create_complete_week_index()."""

    def test_create_complete_week_index_with_family(self, weekly_df):
        """Crea índice completo con familia."""
        agg = DataAggregator()
        
        index_df = agg.create_complete_week_index(weekly_df, group_by_family=True)
        
        assert "store_nbr" in index_df.columns
        assert "family" in index_df.columns
        assert "week_start" in index_df.columns

    def test_create_complete_week_index_without_family(self, weekly_df):
        """Crea índice completo sin familia."""
        agg = DataAggregator()
        
        index_df = agg.create_complete_week_index(weekly_df, group_by_family=False)
        
        assert "store_nbr" in index_df.columns
        assert "family" not in index_df.columns
        assert "week_start" in index_df.columns


class TestDataAggregatorFillMissing:
    """Tests para fill_missing_weeks()."""

    def test_fill_missing_weeks(self, weekly_df):
        """Rellena semanas faltantes con cero."""
        agg = DataAggregator()
        
        # Crear índice completo
        index_df = agg.create_complete_week_index(weekly_df, group_by_family=True)
        
        # Tomar solo un subconjunto para simular huecos
        partial_df = weekly_df.head(10)
        
        # Rellenar huecos
        complete_df = agg.fill_missing_weeks(partial_df, index_df, fill_value=0.0)
        
        assert len(complete_df) >= len(partial_df)
        assert complete_df["sales"].isnull().sum() == 0
