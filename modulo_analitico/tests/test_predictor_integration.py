"""
DEMAND-24 — Tests de Integración: Predictor Full Pipeline
Verificación de cobertura para predictor, agregador, feature builder y trainer.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch

from modulo_analitico.predictor import DemandPredictor
from modulo_analitico.config.ml_config import MLConfig

@pytest.fixture
def synthetic_data():
    """Genera datos sintéticos mínimos para el pipeline."""
    dates = pd.date_range(start="2023-01-01", periods=300, freq="D")
    families = ["BEVERAGES", "DAIRY"]
    
    data = []
    for family in families:
        for date in dates:
            data.append({
                "date": date,
                "store_nbr": 1,
                "family": family,
                "sales": np.random.rand() * 100,
                "onpromotion": 0
            })
    
    train_df = pd.DataFrame(data)
    stores_df = pd.DataFrame([{"store_nbr": 1, "city": "Quito", "type": "D", "cluster": 13}])
    holidays_df = pd.DataFrame([{"date": "2023-01-01", "type": "Holiday", "locale": "National", "locale_name": "Ecuador", "description": "New Year", "transferred": False}])
    oil_df = pd.DataFrame([{"date": d, "dcoilwtico": 75.0} for d in dates])
    
    return train_df, stores_df, holidays_df, oil_df

def test_predictor_full_pipeline_integration(synthetic_data):
    """Prueba el flujo completo del predictor para maximizar la cobertura."""
    train_df, stores_df, holidays_df, oil_df = synthetic_data
    
    from dataclasses import replace
    config = replace(MLConfig(), 
                     PILOT_FAMILIES=["BEVERAGES", "DAIRY"],
                     MIN_WEEKS_HISTORY=2,
                     N_SPLITS=2)
    
    predictor = DemandPredictor(config)
    
    # 1. Mock DataLoader para evitar leer archivos locales
    with patch.object(predictor._data_loader, 'load_all_data', return_value=synthetic_data):
        with patch.object(predictor._data_loader, 'validate_minimum_weeks_per_sku', return_value=(True, "OK")):
            # Ejecutar carga
            predictor.load_data()
            assert predictor._train_df is not None
            
            # 2. Preparar datos (dispara Agregador y FeatureBuilder)
            predictor.prepare_data()
            assert predictor._features_df is not None
            assert len(predictor._features_df) > 0
            
            # Llenar nulos (lags/rolling) para que el entrenador no descarte filas
            predictor._features_df = predictor._features_df.fillna(0)
            
            # 3. Entrenar (dispara Trainer y XGBoost Wrapper)
            metrics = predictor.train(use_cross_validation=True, save_model=False)
            assert "mape_mean" in metrics
            
            # 4. Predecir
            predictions = predictor.predict(weeks_ahead=2)
            assert isinstance(predictions, pd.DataFrame)
            assert len(predictions) > 0
            
            # 5. Evaluar (dispara Evaluator)
            report = predictor.evaluate()
            assert "cumple_ca01" in report

def test_predictor_error_handling():
    """Prueba rutas de error para cubrir bloques except."""
    predictor = DemandPredictor()
    
    # 1. Predecir sin entrenar
    with pytest.raises(RuntimeError, match="Modelo no entrenado"):
        predictor.predict()
    
    # 2. Entrenar sin preparar datos
    with pytest.raises(RuntimeError, match="Datos no preparados"):
        predictor.train()
    
    # 3. Guardar modelo inexistente
    with pytest.raises(RuntimeError, match="No hay modelo"):
        predictor.save_model()

def test_predictor_save_load_integration(tmp_path):
    """Prueba guardado y carga de modelo para cubrir esos métodos."""
    config = MLConfig()
    model_file = tmp_path / "test_model.joblib"
    # Crear el archivo para que path.exists() sea True
    model_file.write_text("dummy content")
    
    predictor = DemandPredictor(config, model_path=model_file)
    
    # Mock de un modelo entrenado
    mock_model = MagicMock()
    predictor._model = mock_model
    predictor._is_ready = True
    
    # Guardar
    predictor.save_model()
    assert mock_model.save.called
    
    # Cargar (Mockeando la carga)
    with patch("modulo_analitico.models.xgboost_model.XGBoostDemandModel.load"):
        with patch("modulo_analitico.models.xgboost_model.XGBoostDemandModel.get_metrics", return_value={"mape": 10.0}):
            predictor.load_model(model_file)
            assert predictor.is_ready
            assert predictor.get_metrics()["mape"] == 10.0
