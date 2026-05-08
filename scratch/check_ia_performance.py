
import sys
import os
from pathlib import Path

# Añadir raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from modulo_analitico.predictor import DemandPredictor
from logica_negocio.core.database import build_session_factory

def run_diagnostic():
    print("INICIANDO DIAGNOSTICO DE IA - DEMAND-24")
    print("=" * 50)
    
    predictor = DemandPredictor()
    
    # 1. Carga de datos
    print("1. Cargando datos reales...")
    predictor.load_data()
    predictor.prepare_data()
    
    # 2. Entrenamiento con Cross-Validation (La prueba de fuego)
    print("2. Ejecutando entrenamiento con 5-Fold Cross-Validation...")
    metrics = predictor.train(use_cross_validation=True, save_model=False)
    
    # 3. Reporte de Resultados
    print("\nREPORTE DE PERFORMANCE")
    print("-" * 50)
    print(f"Error Porcentual (MAPE): {metrics['mape_mean']:.2f}% (+/-{metrics['mape_std']:.2f}%)")
    print(f"Error Absoluto (MAE):    {metrics['mae_mean']:.2f}")
    print(f"Sesgo del Modelo (Bias): {metrics['bias_mean']:.2f}")
    
    # 4. Interpretacion
    print("\nINTERPRETACION DEL ARQUITECTO:")
    if metrics['mape_mean'] < 20:
        print("OK - EXCELENTE: La IA tiene una precision de grado industrial (>80%).")
    elif metrics['mape_mean'] < 40:
        print("OK - ACEPTABLE: La IA detecta tendencias, pero tiene margen de mejora.")
    else:
        print("ALERTA: El error es alto. Se sugiere revisar la calidad de los datos de entrada.")

if __name__ == "__main__":
    run_diagnostic()
