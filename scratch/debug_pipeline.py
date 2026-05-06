import sys
from pathlib import Path
import pandas as pd

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modulo_analitico.data_adapter.loader import DataLoader
from modulo_analitico.data_adapter.aggregator import DataAggregator
from modulo_analitico.data_adapter.feature_builder import FeatureBuilder
from modulo_analitico.config.ml_config import ml_config

def debug():
    loader = DataLoader(ml_config)
    aggregator = DataAggregator(ml_config)
    builder = FeatureBuilder(ml_config)

    print("--- DIAGNÓSTICO DE PIPELINE DEMAND-24 ---")
    
    # 1. Carga
    try:
        train, stores, holidays, oil = loader.load_all_data()
        print(f"1. CARGA: Train: {len(train)} filas, Stores: {len(stores)}, Holidays: {len(holidays)}, Oil: {len(oil)}")
    except Exception as e:
        print(f"ERROR EN CARGA: {e}")
        return

    # 2. Agregación
    weekly = aggregator.aggregate_daily_to_weekly(train)
    print(f"2. AGREGACIÓN: Weekly: {len(weekly)} filas")
    if len(weekly) == 0:
        print("ALERTA: La agregación devolvió 0 filas. Revisa el formato de fecha en train.csv")
        return

    # 3. Features
    features = builder.build_all_features(weekly, stores, holidays, oil)
    print(f"3. FEATURES: Total columns: {len(features.columns)}")
    
    # 4. Limpieza (Lo que el modelo ve)
    cols = builder.get_feature_columns(features)
    clean = features.dropna(subset=cols + ["sales"])
    print(f"4. LIMPIEZA: Quedan {len(clean)} filas después de dropna()")
    
    if len(clean) == 0:
        print("\n--- ¡PROBLEMA DETECTADO! ---")
        null_counts = features[cols + ["sales"]].isnull().sum()
        critical_cols = null_counts[null_counts > 0]
        print("Columnas que están causando el borrado de datos (tienen nulos):")
        print(critical_cols)

if __name__ == "__main__":
    debug()
