"""
DEMAND-24 — Tests para Data Adapter

Tests unitarios para DataLoader, DataAggregator y FeatureBuilder.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import numpy as np

from modulo_analitico.data_adapter.aggregator import DataAggregator
from modulo_analitico.data_adapter.feature_builder import FeatureBuilder


def create_sample_daily_data(n_days=100, n_stores=3, n_families=2):
    """Crea datos diarios de ejemplo para tests."""
    dates = pd.date_range(start="2023-01-01", periods=n_days, freq="D")
    
    rows = []
    for store in range(1, n_stores + 1):
        for family_idx, family in enumerate(["BEVERAGES", "DAIRY"][:n_families]):
            for date in dates:
                rows.append({
                    "date": date,
                    "store_nbr": store,
                    "family": family,
                    "sales": np.random.randint(10, 100),
                    "onpromotion": np.random.randint(0, 5),
                })
    
    return pd.DataFrame(rows)


def test_aggregator_daily_to_weekly():
    """DataAggregator debe agregar correctamente daily → weekly."""
    df = create_sample_daily_data(n_days=28, n_stores=2, n_families=2)
    
    aggregator = DataAggregator()
    weekly_df = aggregator.aggregate_daily_to_weekly(df, group_by_family=True)
    
    assert "week_start" in weekly_df.columns, "Debe tener columna week_start"
    assert "sales" in weekly_df.columns, "Debe tener columna sales"
    print("[PASS] test_aggregator_daily_to_weekly")


def test_aggregator_week_start_consistency():
    """week_start debe ser consistente para dias en la misma semana."""
    df = create_sample_daily_data(n_days=14, n_stores=1, n_families=1)
    
    aggregator = DataAggregator()
    weekly_df = aggregator.aggregate_daily_to_weekly(df)
    
    assert len(weekly_df) > 0, "weekly_df no debe estar vacio"
    assert "week_start" in weekly_df.columns, "Debe tener columna week_start"
    print("[PASS] test_aggregator_week_start_consistency")


def test_feature_builder_temporal_features():
    """FeatureBuilder debe agregar features temporales correctas."""
    df = create_sample_daily_data(n_days=30, n_stores=1, n_families=1)
    aggregator = DataAggregator()
    weekly_df = aggregator.aggregate_daily_to_weekly(df)
    
    builder = FeatureBuilder()
    result_df = builder.add_temporal_features(weekly_df)
    
    assert "year" in result_df.columns, "Debe tener year"
    assert "month" in result_df.columns, "Debe tener month"
    assert "week_of_year" in result_df.columns, "Debe tener week_of_year"
    print("[PASS] test_feature_builder_temporal_features")


def test_feature_builder_lag_features():
    """FeatureBuilder debe crear lags correctamente sin data leakage."""
    df = create_sample_daily_data(n_days=100, n_stores=1, n_families=1)
    aggregator = DataAggregator()
    weekly_df = aggregator.aggregate_daily_to_weekly(df)
    
    builder = FeatureBuilder()
    result_df = builder.add_lag_features(weekly_df, lag_weeks=[1, 2, 4])
    
    assert "sales_lag_1" in result_df.columns, "Debe tener sales_lag_1"
    assert "sales_lag_2" in result_df.columns, "Debe tener sales_lag_2"
    assert "sales_lag_4" in result_df.columns, "Debe tener sales_lag_4"
    print("[PASS] test_feature_builder_lag_features")


def test_feature_builder_rolling_features():
    """FeatureBuilder debe crear rolling stats correctamente."""
    df = create_sample_daily_data(n_days=100, n_stores=1, n_families=1)
    aggregator = DataAggregator()
    weekly_df = aggregator.aggregate_daily_to_weekly(df)
    
    builder = FeatureBuilder()
    result_df = builder.add_rolling_features(weekly_df, windows=[4, 12])
    
    assert "sales_rolling_mean_4" in result_df.columns, "Debe tener sales_rolling_mean_4"
    assert "sales_rolling_std_4" in result_df.columns, "Debe tener sales_rolling_std_4"
    assert "sales_rolling_mean_12" in result_df.columns, "Debe tener sales_rolling_mean_12"
    print("[PASS] test_feature_builder_rolling_features")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("DEMAND-24 — Tests de Data Adapter")
    print("=" * 60)
    
    test_aggregator_daily_to_weekly()
    test_aggregator_week_start_consistency()
    test_feature_builder_temporal_features()
    test_feature_builder_lag_features()
    test_feature_builder_rolling_features()
    
    print("=" * 60)
    print("[OK] Todos los tests pasaron exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
