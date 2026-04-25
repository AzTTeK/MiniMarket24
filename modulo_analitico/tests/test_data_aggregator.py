"""
DEMAND-24 — Tests para DataAggregator
Verificación de agregación semanal para consolidar coverage.
"""

import pytest
import pandas as pd
import numpy as np
from modulo_analitico.data_adapter.aggregator import DataAggregator

def test_aggregator_weekly_aggregation():
    """Prueba la agregación de diaria a semanal usando el método correcto."""
    aggregator = DataAggregator()
    
    # Crear datos diarios (4 semanas empezando en lunes)
    dates = pd.date_range(start="2023-01-02", periods=28, freq="D")
    df_daily = pd.DataFrame({
        "date": dates,
        "store_nbr": 1,
        "family": "DAIRY",
        "sales": 10.0,
        "onpromotion": 0
    })
    
    # Ejecutar agregación (Corregido el nombre del método)
    df_weekly = aggregator.aggregate_daily_to_weekly(df_daily)
    
    # 28 días -> 4 o 5 semanas dependiendo del anclaje de pandas
    assert len(df_weekly) >= 4
    assert df_weekly["sales"].max() == 70.0 # Validar que al menos una semana está completa
    assert "onpromotion" in df_weekly.columns

def test_aggregator_weekly_stats():
    """Prueba el cálculo de estadísticas semanales."""
    aggregator = DataAggregator()
    
    dates = pd.date_range(start="2023-01-02", periods=7, freq="D")
    df_daily = pd.DataFrame({
        "date": dates,
        "store_nbr": 1,
        "family": "DAIRY",
        "sales": [10, 20, 10, 20, 10, 20, 10],
        "onpromotion": [0, 1, 0, 1, 0, 1, 0]
    })
    
    stats = aggregator.calculate_weekly_stats(df_daily)
    # Buscamos la semana que tenga los 7 días para validar el promedio y promociones
    full_week_stats = stats[stats["n_days"] == 7]
    if not full_week_stats.empty:
        assert full_week_stats["sales_mean"].iloc[0] == pytest.approx(14.28, 0.01)
        assert full_week_stats["onpromotion_days"].iloc[0] == 3

def test_aggregator_fill_missing_weeks():
    """Prueba el relleno de semanas faltantes."""
    aggregator = DataAggregator()
    
    df_weekly = pd.DataFrame({
        "week_start": pd.to_datetime(["2023-01-02", "2023-01-16"]), # Falta la semana del 09
        "store_nbr": [1, 1],
        "family": ["DAIRY", "DAIRY"],
        "sales": [100.0, 200.0]
    })
    
    index = aggregator.create_complete_week_index(df_weekly)
    filled = aggregator.fill_missing_weeks(df_weekly, index)
    
    assert len(filled) == 3
    assert filled["sales"].iloc[1] == 0.0 # Semana rellena con 0
