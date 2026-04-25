"""
DEMAND-24 — Tests para DataAggregator
Verificación de agregación semanal para subir coverage.
"""

import pytest
import pandas as pd
import numpy as np
from modulo_analitico.data_adapter.aggregator import DataAggregator

def test_aggregator_weekly_aggregation():
    """Prueba la agregación de diaria a semanal."""
    aggregator = DataAggregator()
    
    # Crear datos diarios
    dates = pd.date_range(start="2023-01-01", periods=14, freq="D")
    df_daily = pd.DataFrame({
        "date": dates,
        "store_nbr": 1,
        "family": "DAIRY",
        "sales": 10.0,
        "onpromotion": 0
    })
    
    # Ejecutar agregación
    df_weekly = aggregator.aggregate_to_weekly(df_daily)
    
    # 14 días -> 2 semanas completas o parciales según el offset
    assert len(df_weekly) >= 2
    assert "sales" in df_weekly.columns
    assert "onpromotion" in df_weekly.columns

def test_aggregator_merge_external_data():
    """Prueba la unión con datos externos."""
    aggregator = DataAggregator()
    
    df_main = pd.DataFrame({
        "date": pd.to_datetime(["2023-01-01"]),
        "store_nbr": [1],
        "family": ["DAIRY"],
        "sales": [10.0]
    })
    
    df_stores = pd.DataFrame({
        "store_nbr": [1],
        "city": ["Quito"]
    })
    
    df_oil = pd.DataFrame({
        "date": pd.to_datetime(["2023-01-01"]),
        "dcoilwtico": ["75.0"]  # El cargador espera string/object
    })
    
    # Unir tiendas
    df_merged = aggregator.merge_stores_data(df_main, df_stores)
    assert "city" in df_merged.columns
    
    # Unir petróleo
    # Nota: la columna en el repo se llama 'oil_price' después del merge interno
    df_merged_oil = aggregator.merge_oil_data(df_main, df_oil)
    assert "oil_price" in df_merged_oil.columns
