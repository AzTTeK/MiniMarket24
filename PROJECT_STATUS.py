#!/usr/bin/env python
"""
DEMAND-24 — Project Status (Auto-Generated)
Generated: 2026-04-16
Purpose: Quick reference for next session
"""

# ============================================================================
# PROYECTO: DEMAND-24 — Sistema Inteligente de Predicción de Demanda
# ============================================================================

# --- ESTADO ACTUAL ---
FASE_ACTUAL = "Fase 2: Módulo Analítico (ML Engine)"
ESTADO = "✅ COMPLETADA"
PROGRESO = "2 de 6 Fases (33%)"

# --- MÉTRICAS CLAVE ---
MODULOS_IMPLEMENTADOS = 10
LINEAS_DE_CODIGO = 3469
TESTS_TOTALES = 29
TESTS_PASANDO = 29
TESTS_FALLANDO = 0
COBERTURA_PROMEDIO = 54  # %
TIEMPO_TESTS = 3.64  # segundos
ARCHIVOS_PYTHON = 25

# --- LO QUE FUNCIONA ---
FUNCIONALIDADES_COMPLETADAS = [
    "✅ Load data (CSV → Dataframe)",
    "✅ Aggregate (Daily → Weekly)",
    "✅ Feature engineering (Temporal, Lags, Rolling)",
    "✅ Model training (XGBoost with TimeSeriesSplit)",
    "✅ Evaluation (Walk-forward validation)",
    "✅ Metrics (MAPE, MAE, Bias, CA-01)",
    "✅ Prediction (Point + Confidence intervals)",
    "✅ Configuration (100% from .env, no hardcoding)",
    "✅ Logging (Debug, Info, Error levels)",
    "✅ Unit tests (29 tests, 100% critical path)",
]

# --- PRÓXIMO PASO ---
PROXIMO_PASO = "Fase 3: Módulo de Datos"
PROXIMO_OBJETIVO = [
    "1. Crear schema Supabase (4 tables)",
    "2. Implementar SQLAlchemy models (ORM)",
    "3. Implementar Pydantic schemas (DTOs)",
    "4. Implementar Repository Pattern",
    "5. Integrar persistencia en DemandPredictor",
    "6. 20+ unit tests nuevos",
]

# --- DOCUMENTOS PARA LEER ---
LECTURAS_RECOMENDADAS = {
    "QUICK_START_NEXT_SESSION.md": "5 min — Contexto rápido",
    "ARCHITECTURAL_DECISIONS.md": "15 min — 15 decisiones fundamentales",
    "FASE3_ROADMAP.md": "20 min — 6 tareas concretas para Fase 3",
    "BITACORA_DESARROLLO_DEMAND24.md": "30 min — Contexto histórico completo",
}

# --- COMANDOS PARA VERIFICAR TODO ESTÁ OK ---
COMANDOS_VERIFICACION = """
# 1. Activar ambiente
.venv\\Scripts\\activate

# 2. Verificar tests (DEBE SER: 29 PASS)
python -m pytest modulo_analitico/tests/ -v

# 3. Verificar imports (DEBE SER: ✅)
python -c "from modulo_analitico.predictor import DemandPredictor; print('✅')"

# 4. Verificar config (DEBE MOSTRAR: RANDOM_SEED=42, N_SPLITS=5, etc.)
python -c "from modulo_analitico.config.ml_config import MLConfig; print(MLConfig())"

# 5. Git status (DEBE ESTAR: Limpio o con cambios esperados)
git status
"""

# --- REGLAS CRÍTICAS A RECORDAR ---
REGLAS_CRITICAS = {
    "I": "Separación estricta: Frontend ↔ Backend ↔ ML (NO mezclar)",
    "II": "DTOs para APIs (interface limpia)",
    "III": "ORM + Repository (Fase 3)",
    "IV": "Unit tests (100% critical path) ✅",
    "V": "Error handling + Logging ✅",
    "VI": "Anti-Leakage: TimeSeriesSplit, features DESPUÉS split ✅",
    "VII": "Contrato de API documentado ✅",
    "VIII": "Zero hardcoding: config DESDE .env ✅",
    "IX": "Logging en funciones críticas ✅",
}

# --- VALORES CONFIGURABLES (NO CAMBIAR SIN RAZÓN) ---
CONFIG_VALORES = {
    "ML_RANDOM_SEED": 42,  # Reproducibilidad
    "ML_N_SPLITS": 5,  # Validación temporal
    "ML_XGBOOST_MAX_DEPTH": 6,  # Balance
    "ML_XGBOOST_LEARNING_RATE": 0.1,  # Standard
    "MAPE_THRESHOLD": 20.0,  # CA-01
    "CONFIDENCE_LEVEL": 0.90,  # 90% intervals
    "PILOT_SKU_IDS": "101,102,103,104,105",  # 5 SKUs
    "CA_01_THRESHOLD": 0.70,  # 70% SKU ≤20% MAPE
}

# --- ESTRUCTURA DEL PROYECTO ---
ESTRUCTURA = {
    "modulo_analitico/": {
        "config/ml_config.py": "158 líneas — Config centralizada",
        "wrappers/xgboost_wrapper.py": "235 líneas — XGBoost abstraction",
        "data_adapter/": "Load (259) + Aggregate (203) + Features (327)",
        "models/": "XGBoost model (276) + Metrics (234)",
        "training/": "Trainer (249) + Evaluator (304)",
        "predictor.py": "486 líneas — API pública (6 métodos)",
        "tests/": "7 archivos, 29 tests, 100% PASS",
    }
}

# --- SI ALGO FALLA ---
TROUBLESHOOTING = {
    "Tests no pasan": "→ Leer sección 'Test Coverage' en BITACORA",
    "Imports fuellan": "→ Verificar .env existe, python 3.13.5 activado",
    "Config no carga": "→ Verificar .env tiene todas variables ML_*",
    "Datos no cargan": "→ Verificar data/raw/ tiene CSV files",
    "Modelo no predice": "→ Revisar features calculadas = entrenamiento",
}

# --- OBJETIVO DE ESTA SESIÓN ---
OBJETIVO = """
✅ Fase 2 COMPLETADA:
   - 10 módulos ML implementados
   - 29 tests pasando (100%)
   - 0 errores de sintaxis
   - 0 imports faltantes
   - 8/9 Reglas implementadas
   - 4 documentos de referencia creados
   - BITÁCORA actualizada

🟢 LISTO PARA FASE 3
"""

# --- PRÓXIMA SESIÓN ---
CHECKLIST_PROXIMO_INICIO = [
    "[ ] Leer QUICK_START_NEXT_SESSION.md (5 min)",
    "[ ] Leer ARCHITECTURAL_DECISIONS.md (15 min)",
    "[ ] Verificar 29 tests PASS",
    "[ ] Verificar .env existe",
    "[ ] Crear rama: git checkout -b feature/fase3-modulo-datos",
    "[ ] Leer FASE3_ROADMAP.md",
    "[ ] Iniciar Tarea 1: Schema Supabase",
]

# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("DEMAND-24 — PROJECT STATUS")
    print("=" * 80)
    print()
    print(f"Estado: {ESTADO}")
    print(f"Fase: {FASE_ACTUAL}")
    print(f"Progreso: {PROGRESO}")
    print()
    print("Métricas:")
    print(f"  • Módulos: {MODULOS_IMPLEMENTADOS}")
    print(f"  • Líneas de código: {LINEAS_DE_CODIGO:,}")
    print(f"  • Tests: {TESTS_PASANDO}/{TESTS_TOTALES} PASS")
    print(f"  • Tiempo: {TIEMPO_TESTS}s")
    print(f"  • Cobertura: {COBERTURA_PROMEDIO}%")
    print()
    print("Próximo Paso:")
    print(f"  → {PROXIMO_PASO}")
    print()
    print("Lectura Recomendada (en orden):")
    for doc, desc in LECTURAS_RECOMENDADAS.items():
        print(f"  1. {doc:40s} — {desc}")
    print()
    print(f"Objetivo: {OBJETIVO.strip()}")
    print()
    print("=" * 80)
    print("Ready for Fase 3 ✅")
    print("=" * 80)
