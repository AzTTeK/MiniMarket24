"""
DEMAND-24 — Tests para DataLoader
Verificación de carga de archivos CSV para subir coverage de loader.py.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from modulo_analitico.data_adapter.loader import DataLoader

@pytest.fixture
def temp_csv_files(tmp_path):
    """Crea archivos CSV temporales para pruebas de carga."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # train.csv
    train_path = data_dir / "train.csv"
    pd.DataFrame({
        "id": [0, 1],
        "date": ["2023-01-01", "2023-01-02"],
        "store_nbr": [1, 1],
        "family": ["DAIRY", "DAIRY"],
        "sales": [10.0, 20.0],
        "onpromotion": [0, 1]
    }).to_csv(train_path, index=False)
    
    # stores.csv
    stores_path = data_dir / "stores.csv"
    pd.DataFrame({
        "store_nbr": [1],
        "city": ["Quito"],
        "state": ["Pichincha"],
        "type": ["D"],
        "cluster": [13]
    }).to_csv(stores_path, index=False)
    
    # oil.csv
    oil_path = data_dir / "oil.csv"
    pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "dcoilwtico": ["75.0", "76.0"] # Debe ser string/object
    }).to_csv(oil_path, index=False)
    
    # holidays_events.csv
    holidays_path = data_dir / "holidays_events.csv"
    pd.DataFrame({
        "date": ["2023-01-01"],
        "type": ["Holiday"],
        "locale": ["National"],
        "locale_name": ["Ecuador"],
        "description": ["New Year"],
        "transferred": ["False"] # Debe ser string/object
    }).to_csv(holidays_path, index=False)
    
    return data_dir

def test_dataloader_load_methods(temp_csv_files):
    """Prueba los métodos individuales de carga para subir coverage."""
    from dataclasses import replace
    from modulo_analitico.config.ml_config import MLConfig
    
    # Inyectar la ruta temporal en la config
    config = replace(MLConfig(), DATA_RAW_DIR=temp_csv_files)
    loader = DataLoader(config=config)
    
    # Probar cargas individuales que estaban en 0%
    df_train = loader.load_train_data()
    assert len(df_train) == 2
    
    df_stores = loader.load_stores_data()
    assert len(df_stores) == 1
    
    df_oil = loader.load_oil_data()
    assert len(df_oil) == 2
    
    df_holidays = loader.load_holidays_data()
    assert len(df_holidays) == 1
    
    # Probar validación de semanas
    # Con solo 2 días, esto debería devolver False
    is_ok, msg = loader.validate_minimum_weeks_per_sku(df_train, min_weeks=2)
    assert not is_ok
    assert "menos de 2 semanas" in msg

def test_dataloader_file_not_found(tmp_path):
    """Prueba error cuando no existen archivos."""
    from dataclasses import replace
    from modulo_analitico.config.ml_config import MLConfig
    
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    config = replace(MLConfig(), DATA_RAW_DIR=empty_dir)
    loader = DataLoader(config=config)
    
    with pytest.raises(FileNotFoundError):
        loader.load_train_data()
