# ⚡ REFERENCIA RÁPIDA — PRÓXIMA SESIÓN

**Fecha de cierre**: 16 de abril de 2026  
**Estado**: Fase 2 ✅ COMPLETADA | Próximo: Fase 3 (Módulo de Datos)

---

## 🎯 CONTEXTO EN 30 SEGUNDOS

**Proyecto**: DEMAND-24 — Predicción de demanda para MiniMarket La 24  
**Tecnología**: Python 3.13.5 + XGBoost + Supabase + FastAPI + React  
**Arquitectura**: Separación estricta (Frontend → Backend Logic → ML Engine)

### ✅ LO QUE YA EXISTE

- **Modulo Analítico**: 10 módulos, 3,469 líneas de código
- **Tests**: 29 tests, 100% PASS (3.64 seg)
- **Configuración**: 100% desde .env (Regla VIII)
- **Pipeline ML**: load → aggregate → feature → train → evaluate → predict

### ⏳ QUÉ FALTA (Fase 3)

- Esquema en Supabase
- Repository Pattern (ORM + SQLAlchemy)
- Persistencia de predicciones
- Connect Modulo Analítico ↔ BD

---

## 📂 ESTRUCTURA CLAVE

```
modulo_analitico/           # ML Engine (COMPLETADO ✅)
├── config/ml_config.py      # Config desde .env
├── data_adapter/            # Load, Aggregate, Features
├── models/                  # XGBoost, Metrics, CA-01
├── training/                # Trainer, WalkForwardEvaluator
└── tests/                   # 29 tests passing

logica_negocio/             # Backend Business Logic (TODO)
├── database/
│   ├── models/              # SQLAlchemy ORM — IMPLEMENTAR
│   ├── repositories/        # Repository Pattern — IMPLEMENTAR
│   └── schemas/             # Pydantic DTOs — IMPLEMENTAR
└── config/settings.py       # Supabase credentials

.env                        # Variables de entorno
.env.example                # Template
```

---

## 🚀 ARRANQUE RÁPIDO

```bash
# 1. Navegar
cd c:\Users\users\Desktop\ELÍAS\Minimarket24

# 2. Activar ambiente
.venv\Scripts\activate

# 3. Verificar tests OK
python -m pytest modulo_analitico/tests/ -v

# 4. Verificar imports OK
python -c "from modulo_analitico.predictor import DemandPredictor; print('✅')"

# 5. Verificar config OK
python -c "from modulo_analitico.config.ml_config import MLConfig; print(MLConfig())"
```

**Si todo ✅**: Proceder a Fase 3

---

## 🔑 9 REGLAS DE BUENAS PRÁCTICAS

| # | Regla | Estado |
|----|-------|--------|
| I | Separación Estricta (LLM: UI ↔ Backend ↔ ML) | ✅ |
| II | DTOs para APIs | ✅ |
| III | ORM + Repository | ⏳ **PRÓXIMO** |
| IV | Unit Tests (100% critical path) | ✅ |
| V | Error Handling + Logging | ✅ |
| VI | Anti-Leakage (TimeSeriesSplit) | ✅ |
| VII | Contrato de API documentado | ✅ |
| VIII | Zero Hardcoding (config desde .env) | ✅ |
| IX | Logging en funciones críticas | ✅ |

---

## 🎓 REGLA VI CRÍTICA (Anti-Leakage)

⚠️ **NUNCA hacer esto en Fase 3:**
```python
# ❌ MAL — Features antes del split
features = calculate_features(all_data)
train_data = timeserieplit(features)

# ✅ CORRECTO — Features después del split
train_data = timeseriessplit(all_data)
features = calculate_features_per_split(train_data)
```

---

## 📊 PIPELINE ML ACTUAL

```
CSV (raw)
   ↓ [DataLoader]
Dataframe (cleaned)
   ↓ [DataAggregator] — Daily → Weekly (W-MON)
Weekly data
   ↓ [FeatureBuilder] — Temporal, Lags, Rolling
Features ready
   ↓ [TimeSeriesSplit] — NO LEAKAGE
Train | Test splits
   ↓ [ModelTrainer]
XGBoost model (fitted)
   ↓ [WalkForwardEvaluator]
Metrics (MAPE, MAE, Bias, CA-01)
   ↓ [DemandPredictor → Predicciones puntuales + IC]
Output: predictions JSON
```

---

## 🛠️ APIs PÚBLICAS A RECORDAR

### DemandPredictor (modulo_analitico/predictor.py)

```python
from modulo_analitico.predictor import DemandPredictor

predictor = DemandPredictor()
predictor.load_data()                   # Lee CSV
predictor.prepare_data()                # Load + Aggregate + Features
results = predictor.train()             # Entrena modelo
predictions = predictor.predict(weeks=4) # Predicciones futuras
metrics = predictor.get_evaluation_metrics()

# En Fase 3: Guardar results y predictions en BD
```

---

## 🔧 CONFIGURACIÓN DESDE .env

```env
# ML (Reproducibilidad)
ML_RANDOM_SEED=42
ML_N_SPLITS=5
ML_CONFIDENCE_LEVEL=0.90

# XGBoost
ML_XGBOOST_MAX_DEPTH=6
ML_XGBOOST_LEARNING_RATE=0.1
ML_XGBOOST_N_ESTIMATORS=100
ML_XGBOOST_SUBSAMPLE=0.8
ML_XGBOOST_COLSAMPLE_BYTREE=0.8

# Negocio
PILOT_SKU_IDS=101,102,103,104,105
MIN_WEEKS_HISTORY=12
MAPE_LOW_CONFIDENCE_THRESHOLD=25.0
```

---

## 📝 TODO PARA FASE 3

- [ ] Crear tables Supabase (sku, prediction_history, fold_metrics)
- [ ] Implementar `logica_negocio/database/models/` (SQLAlchemy)
- [ ] Implementar `logica_negocio/database/repositories/` (Repository Pattern)
- [ ] Implementar `logica_negocio/database/schemas/` (Pydantic DTOs)
- [ ] Tests para repositories
- [ ] Integrar persistencia en DemandPredictor
- [ ] Completar Regla III

---

## 📖 DOCUMENTACIÓN INTERNA

```
Documents/
├── BITACORA_DESARROLLO_DEMAND24.md ← **LEE ESTO PRIMERO**
│   └─ Estado actual, cambios, decisiones, 13 secciones
├── SRS_MINIMARKET_DETALLADO_Optimized.md
│   └─ Requerimientos funcionales (RF-01 a RF-04)
├── DEMAND24_Arquitectura_Modular_Optimized.md
│   └─ Vista arquitectónica completa
└── QUICK_START_NEXT_SESSION.md ← **ESTÁS AQUÍ**
```

---

## ⚠️ PUNTOS CRÍTICOS A RECORDAR

1. **Regla VI (Anti-Leakage)**: Features DESPUÉS del split temporal
2. **Regla VIII (Zero Hardcoding)**: TODO desde .env
3. **CA-01**: 70% SKU con MAPE ≤ 20% (implementado + testeado)
4. **Random Seed 42**: Para reproducibilidad
5. **TimeSeriesSplit**: Obligatorio, no random shuffle
6. **MAPE Especial**: Maneja ceros como |actual| < 1e-10

---

## 🧪 TESTS CRÍTICOS QUE NO DEBEN FALLAR

```bash
# Anti-Leakage check
pytest modulo_analitico/tests/test_trainer.py::test_trainer_train_success -v

# Metrics check
pytest modulo_analitico/tests/test_metrics.py::test_check_acceptance_criteria_pass -v

# Data pipeline check
pytest modulo_analitico/tests/test_data_adapter.py -v

# Full integration check
python -m pytest modulo_analitico/tests/ -v
```

Todos deben pasar. Si falla alguno: **STOP — Revisar BITÁCORA sección relevante**

---

## 💾 GIT WORKFLOW SUGERIDO

```bash
# Antes de Fase 3
git checkout -b feature/fase3-modulo-datos
git add .
git commit -m "Fase 2 completada: 29 tests passing, 10 modules, 3.4K LOC"
git push

# Durante Fase 3
git commit -m "Fase 3: Implement SkuRepository, PredictionRepository"
git commit -m "Fase 3: Add Supabase schema + SQLAlchemy models"
# ... iterations ...
```

---

## 🆘 SI ALGO EXPLOTA

1. Leer sección relevante de BITÁCORA
2. Ejecutar `pytest modulo_analitico/tests/ -v` (¿siguen 29/29 PASS?)
3. Si tests fallan: Revertar cambios recientes
4. Si tests OK pero falla integración: Revisar imports y config
5. **NUNCA** cambiar XGBoost hyperparams sin razón válida

---

## ✅ CHECKLIST PRE-INICIO FASE 3

- [ ] Python 3.13.5 activado
- [ ] 29 tests PASS
- [ ] Imports OK
- [ ] .env configurado (o .env.example visible)
- [ ] BITÁCORA leída completamente
- [ ] Rama Git creada: `feature/fase3-modulo-datos`
- [ ] Supabase CLI/SDK installed (`pip install supabase`)
- [ ] Arquitectura Modular doc entendida

**Si ✅ TODO**: Ready to start Fase 3 con confianza total.

---

**Última actualización**: 16 de abril de 2026  
**Fase**: 2 (Completada) → 3 (Por iniciar)  
**Estado**: 🟢 TODO LISTO
