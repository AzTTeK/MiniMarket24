# DECISIONES ARQUITECTÓNICAS — DEMAND-24

**Última actualización**: 21 de abril de 2026  
**Validez**: Estas decisiones aplican para todas las fases futuras salvo cambio explícito

---

## 1. SEPARACIÓN ESTRICTA DE CAPAS (Regla I)

**Decisión**: Las 3 capas NUNCA deben mezclarse.

```
┌─ CAPA 1: VISUALIZACIÓN ─────────────┐
│ Frontend (React + Vite)             │
│ - Solo renderiza UI                 │
│ - Consume REST API                  │
│ - CERO lógica de negocio            │
│ - CERO código ML                    │
└─────────────────────────────────────┘
           ↓ HTTP REST API
┌─ CAPA 2: LÓGICA DE NEGOCIO ────────┐
│ Backend (FastAPI + SQLAlchemy)     │
│ - Gestión de alertas                │
│ - Reglas de negocio                 │
│ - Persistencia (Supabase)           │
│ - Orquestación                      │
│ - CERO código ML directo            │
│  (accede a ML via DemandPredictor)  │
└─────────────────────────────────────┘
           ↓ Python import
┌─ CAPA 3: ML ENGINE ────────────────┐
│ Módulo Analítico (XGBoost)         │
│ - Data processing                   │
│ - Feature engineering               │
│ - Training                          │
│ - Prediction                        │
│ - CERO conocimiento de BD           │
│ - CERO conocimiento de UI           │
└─────────────────────────────────────┘
```

**Por qué**: Si Frontend quiere datos ML, va a Backend (que luego va a ML). Así garantizamos que cada capa es independiente y reemplazable.

**Garantía**: Si cambias BD de Supabase a PostgreSQL puro, Frontend no se entera. Si cambias ML Engine de XGBoost a LightGBM, BD no se entera.

---

## 2. CONFIGURACIÓN 100% DESDE .env (Regla VIII)

**Decisión**: NUNCA hardcodear valores que cambien entre ambientes.

**Valores que DEBEN estar en .env**:
- Credenciales BD
- URLs de APIs
- Hiperparámetros ML (MAX_DEPTH, LEARNING_RATE, etc.)
- Umbrales de negocio (MAPE_THRESHOLD)
- SKU Piloto IDs
- Random seeds

**Valores que PUEDEN ser constantes en código**:
- Estrategia de validación (TimeSeriesSplit)
- Nombres de features (year, month, etc.)
- Fórmulas matemáticas (MAPE = mean(|a-p|/|a|)*100)

**Verificación**: `grep -r "^[A-Z_]+ = \"[0-9.]" modulo_analitico/` debe retornar CERO ← Si retorna algo, es hardcoding ilegal.

---

## 3. VALIDACIÓN TEMPORAL — TimeSeriesSplit SIEMPRE (Regla VI)

**Decisión**: NUNCA usar random shuffle para validación de series de tiempo.

**Flujo CORRECTO**:
```
1. Cargar datos históricos
2. Aplicar TimeSeriesSplit (5 folds por defecto)
3. Para cada fold:
   a. Train con semanas previas
   b. Validar con semanas futuras (NUNCA futuras en train)
   c. Validate con temporal split (test después de train en el tiempo)
4. Agregar todas predicciones
5. Calcular métricas globales
```

**Flujo INCORRECTO**:
```
Usar datos de mes 12 para entrenar y mes 1 para probar
❌ Calcular features con data futura
```

**Por qué**: Con datos de series de tiempo, validar con datos futuros = **data leakage** = evaluación falsamente optimista.

---

## 4. CRITERIO CA-01 — NUNCA CAMBIAR

**Decisión**: El criterio de aceptación es NEGOCIO, no técnico.

**CA-01**: 70% de SKUs deben tener MAPE ≤ 20%

**Por qué 70%?**: Porque el negocio dijo "queremos que al menos 70% de productos sean predecibles con 20% de error o menos".

**Implementación**: Función `check_acceptance_criteria()` en `models/metrics.py`

```python
def check_acceptance_criteria(metrics_by_sku: dict) -> bool:
    """Verificar CA-01: 70%+ SKU with MAPE ≤ 20%."""
    total_skus = len(metrics_by_sku)
    good_skus = sum(1 for m in metrics_by_sku.values() if m['mape'] <= 20.0)
    return (good_skus / total_skus) >= 0.70
```

**NUNCA hacer**: Cambiar threshold a 75% o 50% sin aprobación de negocio.

---

## 5. MAPE ESPECIAL — Manejo de Ceros

**Decisión**: MAPE = mean(|actual - predicted| / |actual|) * 100, pero con handling especial.

**Regla**: Si |actual| < 1e-10 (prácticamente 0):
- Si predicted ≈ 0 también → error = 0 (predicción correcta)
- Si predicted ≠ 0 → error = 100 (predicción incorrecta)

**Por qué**: MAPE tradicional = inf cuando divisor es 0. Negocio necesita interpretable.

**Código**:
```python
def calculate_mape(actual, predicted):
    mask = np.abs(actual) < 1e-10
    mape = np.mean(np.abs((actual - predicted) / np.where(mask, 1, actual))) * 100
    mape = np.where(mask & (np.abs(predicted) > 1e-10), 100, mape)
    return mape
```

---

## 6. REPRODUCIBILIDAD — Random Seed FIJO

**Decisión**: `ML_RANDOM_SEED=42` (fijo, no variable)

**Por qué**: Cada vez que alguien entrena el modelo, debe obtener EXACTO mismo resultado. Facilita debugging, comparación de cambios, etc.

**Dónde se usa**:
```python
config = MLConfig()
np.random.seed(config.RANDOM_SEED)
xgboost.XGBRegressor(random_state=config.RANDOM_SEED)
```

**NUNCA hacer**: Usar `random.seed()` cada vez. Usar centralizado en `MLConfig` siempre.

---

## 7. ARQUITECTURA XGBoost — Wrapper + Model + Trainer

**Decisión**: 3 capas de abstracción para XGBoost.

```python
Capa 1: XGBoostModelWrapper        (wraps XGBRegressor)
        └─ .fit()
        └─ .predict()
        └─ .feature_importances()
        
Capa 2: XGBoostDemandModel         (orchestrator)
        └─ .fit(X, y, features_cols, hyperp)
        └─ .predict(X)
        └─ .save() / .load()
        
Capa 3: ModelTrainer               (with validation split)
        └─ .train(data, sku_ids)
        └─ Returns: model, metrics, predictions
```

**Por qué**: 
- Wrapper = reemplazable (cambiar XGBoost → LightGBM)
- Model = orchestrator
- Trainer = validación + anti-leakage

**NUNCA hacer**: Usar XGBRegressor directamente en código. Siempre via wrapper.

---

## 8. PERSISTENCIA — ¿Dónde guardar modelos?

**Decisión**: Modelos en disco (joblib), metadata en BD (Supabase).

```
Modelo binario (.pkl):
└─ modulo_analitico/models/saved/xgboost_v1.pkl
   └─ Solo internamente, no versionado en Git

Metadata (Supabase):
└─ model_version table
   └─ version, training_date, random_seed, hyperparams, acceptance_criteria_met
   └─ VERSIONADO, AUDITABLE
```

**Por qué**: Modelos binarios son pesados (GB), Git no es BD. BD para audit trail.

---

## 9. PIPELINE ML — NO TOCAR ORDEN

**Decisión**: Pipeline es lineal, no se puede saltar pasos.

```
CSV → Load → Aggregate → Feature → Split → Train → Validate → Predict → Save
```

**Cada paso DEPENDE del anterior**:
- Aggregate: requiere Load (dataframe limpio)
- Feature: requiere Aggregate (weekly data)
- Split: requiere Feature (features listas, sin leakage)
- Train: requiere Split (train/test separados)
- Validate: requiere Train (modelo fitted)
- Predict: requiere Feature (features iguales a train)
- Save: requiere Predict (datos para auditar)

**NUNCA hacer**: 
- Saltarse Feature (usar raw data en ML)
- Feature antes de Split (data leakage)
- Predict con features diferentes a train

---

## 10. API PÚBLICA DemandPredictor — Contrato

**Decisión**: 6 métodos públicos, resto private.

```python
class DemandPredictor:
    # PUBLIC (consumidos por Backend + Tests)
    def load_data(self) → None
    def prepare_data(self) → None
    def train(self) → dict
    def predict(weeks_ahead: int) → pd.DataFrame
    def train_batch(sku_ids: List[str]) → dict
    def get_evaluation_metrics(self) → dict
    
    # PRIVATE (internos)
    def _train_internal() → dict
    def _validate_data() → bool
    def _compute_interval_bounds() → Tuple[float, float]
```

**Garantía**: Si Backend usa solo los 6 públicos, puedo refactorizar privados sin breaking change.

**NUNCA hacer**: Backend accediendo a métodos comenzados con `_` (private).

---

## 11. EVALUACIÓN — WalkForward vs Train/Test Split

**Decisión**: Usar WalkForwardEvaluator, NO simple train/test split.

**Walk Forward**:
```
Fold 1: Train [1-50], Test [51-55]
Fold 2: Train [1-55], Test [56-60]
Fold 3: Train [1-60], Test [61-65]
...
└─ Cada fold usa todo el histórico hasta ese punto
└─ Simula "predecir el futuro" realista
```

**Simple split** (❌ NO):
```
Train [1-80], Test [81-100]
└─ ML ve futuro (leakage) si features no son cleaned
```

**Por qué**: Walk Forward simula cómo el modelo funcionaría en producción: entrenar con histórico, predecir futuro nuevo.

---

## 12. INTEGRACIÓN CON FASE 4 (FastAPI)

**Decisión**: Backend accede a ML via `DemandPredictor`, NO directo.

```python
# CORRECTO (Fase 4)
from modulo_analitico.predictor import DemandPredictor

@app.post("/train")
def train_endpoint(db_session):
    predictor = DemandPredictor()
    predictor.load_data()
    predictor.prepare_data()
    results = predictor.train()
    # Guardar en BD via Repository
    return results

# INCORRECTO
from modulo_analitico.models.xgboost_model import XGBoostDemandModel
model = XGBoostDemandModel()  # Backend no debe instanciar directo
```

**Por qué**: DemandPredictor es el contrato. Si Backend toca internos, rompemos Regla I.

---

## 13. ERROR HANDLING — Be Loud, Fail Fast

**Decisión**: Errores DEBEN loguear + propagarse, no silenciar.

```python
try:
    data = load_csv("data/raw/train.csv")
except FileNotFoundError:
    logger.error("Dataset missing: data/raw/train.csv")
    raise  # ← Propagar, NO silenciar

try:
    predictions = model.predict(X_test)
except Exception as e:
    logger.error(f"Prediction failed: {str(e)}")
    raise
```

**NUNCA hacer**:
```python
try:
    data = load_csv()
except:
    pass  # ← HORRIBLE, error silenciado
```

---

## 14. TESTING — Cobertura de Crítico

**Decisión**: 100% cobertura de critical path (fit, predict, evaluate). Otros pueden ser < 100%.

**Critical path**: 
- FeatureBuilder: temporal, lag, rolling features
- Metrics: MAPE, CA-01
- ModelTrainer: train con TimeSeriesSplit
- DemandPredictor: load, train, predict
- WalkForwardEvaluator: evaluate

**No-critical (pero bueno tener)**:
- save/load model
- batch operations
- formatting output

**Métrica**: Total 29 tests, critical path 100% passing. Mantenible.

---

## 15. LOGGING — DEBUG vs INFO vs ERROR

**Decisión**: 3 niveles de logging únicamente.

```python
logger.debug("Feature X computed for SKU Y")  # Development
logger.info("Training started with 100 samples")  # Execution flow
logger.error("Cannot load CSV: permission denied")  # Problems
```

**NUNCA hacer**:
```python
logger.warning(...)  # Usar ERROR en su lugar
print("Debug info")  # Usar logger.debug()
```

**Dónde loguear**: Puntos clave (entrada/salida de métodos, errores, métricas).

---

## CAMBIOS FUTUROS ESPERADOS

Estas decisiones son ESTABLES. Los cambios esperados cuando evolucionemos:

1. **Fase 3**: Agregar ORM + Repository (Regla III)
2. **Fase 4**: Agreggar FastAPI endpoints (consume DemandPredictor)
3. **Fase 5**: Agregar React UI (consume REST API)
4. **Fase 6**: Docker + CI/CD

Pero **NUNCA**:
- Cambiar separación de capas
- Tocar TimeSeriesSplit strategy
- Hardcodear config
- Cambiar CA-01 sin razón

---

## CHECKLIST DE DECISIONES

Al iniciar nuevas sesiones, verificar:

- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]
- [ ]

Si la respuesta a TODAS es Correcto: Proceed. Si alguna es Incorrecto: Review decisión.

---

## 16. PERSISTENCIA — SQLAlchemy 2.0 & Repository Pattern

**Decisión**: Usar el patrón Repository para desacoplar modelos ORM de la lógica de negocio.

**Estructura**:
- **Schemas (Pydantic)**: Contratos de datos (DTOs).
- **Models (SQLAlchemy)**: Definición de tablas.
- **Repositories**: Clases especializadas en CRUD y operaciones masivas.

**Por qué**: Permite cambiar la base de datos (ej: de Postgres a MariaDB) o el ORM sin tocar una sola línea del motor de IA o de la API.

---

## 17. SUPABASE COMO FUENTE DE VERDAD (System of Record)

**Decisión**: Supabase es el destino final de todos los datos procesados y predicciones.

**Reglas**:
- Los CSV locales son para **entrenamiento masivo** (velocidad).
- La BD es para **operación diaria** y auditoría.
- Toda predicción generada de forma oficial DEBE persistirse en la tabla `prediction`.

---

## 18. INYECCIÓN DE DEPENDENCIA DE BASE DE DATOS

**Decisión**: La sesión de base de datos se inyecta desde la capa superior (Backend) a los repositorios o al predictor.

**Código**:
```python
# DemandPredictor no crea la sesión, la recibe
def save_predictions(self, session: Session):
    repo = PredictionRepository(session)
    # ...
```

**Por qué**: Facilita enormemente el testing unitario (usando bases de datos en memoria como SQLite) sin afectar el código de producción.

---

**Versión**: 1.1  
**Próxima revisión**: Antes de Fase 4  
**Autoridad**: Equipo DEMAND-24
