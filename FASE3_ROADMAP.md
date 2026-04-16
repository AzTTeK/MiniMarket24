# FASE 3 — MÓDULO DE DATOS (Data + Persistence Layer)

**Estado**: ⏳ Por iniciar (después de Fase 2 ✅)  
**Duración estimada**: 1-2 sesiones  
**Objetivo**: Conectar ML Engine con base de datos (Supabase) usando Repository Pattern

---

## 🎯 OBJETIVO FASE 3

Implementar la **capa de persistencia** entre el Módulo Analítico (que genera predicciones) y Supabase (que las almacena), cumpliendo Regla III (ORM + Repository).

```
Módulo Analítico (genera predicciones)
            ↓
        [FASE 3 → AQUÍ]
            ↓
    logica_negocio/database/
        ├── models/     (SQLAlchemy ORM)
        ├── repositories/ (Repository Pattern)
        └── schemas/    (Pydantic DTOs)
            ↓
      Supabase (almacena datos)
```

---

## 📋 TAREAS FASE 3

### **TAREA 1: Schema SQL en Supabase**

**Qué hacer**: Crear tables en Supabase para:

```sql
-- 1. SKU Information
CREATE TABLE sku (
    id BIGSERIAL PRIMARY KEY,
    sku_code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Predicciones (main table)
CREATE TABLE prediction (
    id BIGSERIAL PRIMARY KEY,
    sku_id BIGINT REFERENCES sku(id),
    week_start DATE NOT NULL,
    predicted_demand NUMERIC(10, 2) NOT NULL,
    confidence_level NUMERIC(3, 2),
    lower_bound NUMERIC(10, 2),
    upper_bound NUMERIC(10, 2),
    mape NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(sku_id, week_start)
);

-- 3. Histórico de evaluaciones
CREATE TABLE evaluation_fold (
    id BIGSERIAL PRIMARY KEY,
    fold_number INT NOT NULL,
    sku_id BIGINT REFERENCES sku(id),
    mape NUMERIC(5, 2),
    mae NUMERIC(10, 2),
    bias NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Modelos entrenados (metadata)
CREATE TABLE model_version (
    id BIGSERIAL PRIMARY KEY,
    version VARCHAR(20) UNIQUE NOT NULL,
    training_date TIMESTAMP DEFAULT NOW(),
    random_seed INT,
    n_splits INT,
    xgboost_params JSONB,
    acceptance_criteria_met BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Donde**: Supabase Dashboard → SQL Editor → Run each CREATE TABLE  
**Verificación**: `SELECT * FROM pg_tables WHERE schemaname = 'public'`

**Puntaje**: ✅ Task 1 completa cuando Supabase tiene 4 tables

---

### **TAREA 2: SQLAlchemy Models**

**Ubicación**: `logica_negocio/database/models/`

**Crear**: `sku.py`, `prediction.py`, `evaluation_fold.py`, `model_version.py`

```python
# logica_negocio/database/models/sku.py
from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Sku(Base):
    __tablename__ = "sku"
    
    id = Column(BigInteger, primary_key=True)
    sku_code = Column(String(20), unique=True, nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Similar para Prediction, EvaluationFold, ModelVersion
```

**Requisitos**:
- [ ] Todos los models heredan de `declarative_base()`
- [ ] Todas las relaciones están definidas
- [ ] Timestamps automáticos (created_at, updated_at)
- [ ] Constraints SQL respetados (UNIQUE, FOREIGN KEY, etc.)

**Puntaje**: ✅ Task 2 completa cuando 4 models existen + testean

---

### **TAREA 3: Pydantic Schemas (DTOs)**

**Ubicación**: `logica_negocio/database/schemas/`

**Crear**: `sku.py`, `prediction.py`, etc.

```python
# logica_negocio/database/schemas/prediction.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PredictionCreate(BaseModel):
    sku_id: int
    week_start: date
    predicted_demand: float
    confidence_level: float
    lower_bound: float
    upper_bound: float
    mape: float

class PredictionRead(PredictionCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2
```

**Requisitos**:
- [ ] Read schemas (para GET)
- [ ] Create schemas (para POST)
- [ ] Update schemas (para PATCH)
- [ ] Validaciones Pydantic (@validator si es necesario)
- [ ] from_attributes=True para convertir ORM → JSON

**Puntaje**: ✅ Task 3 completa cuando esquemas se validan (test: DTO parsing)

---

### **TAREA 4: Repository Pattern**

**Ubicación**: `logica_negocio/database/repositories/`

**Crear**: `sku_repository.py`, `prediction_repository.py`, etc.

```python
# logica_negocio/database/repositories/prediction_repository.py
from sqlalchemy.orm import Session
from logica_negocio.database.models.prediction import Prediction
from logica_negocio.database.schemas.prediction import PredictionCreate, PredictionRead
from typing import List, Optional

class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, prediction: PredictionCreate) -> PredictionRead:
        """Crear nueva predicción."""
        db_prediction = Prediction(**prediction.dict())
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        return PredictionRead.from_orm(db_prediction)
    
    def get_by_sku_week(self, sku_id: int, week_start: date) -> Optional[PredictionRead]:
        """Obtener predicción por SKU y semana."""
        result = self.db.query(Prediction).filter_by(
            sku_id=sku_id, week_start=week_start
        ).first()
        return PredictionRead.from_orm(result) if result else None
    
    def get_all_by_sku(self, sku_id: int) -> List[PredictionRead]:
        """Obtener todas predicciones de un SKU."""
        results = self.db.query(Prediction).filter_by(sku_id=sku_id).all()
        return [PredictionRead.from_orm(r) for r in results]
    
    def bulk_create(self, predictions: List[PredictionCreate]) -> List[PredictionRead]:
        """Insertar múltiples predicciones (para batch)."""
        db_predictions = [Prediction(**p.dict()) for p in predictions]
        self.db.add_all(db_predictions)
        self.db.commit()
        return [PredictionRead.from_orm(p) for p in db_predictions]
```

**Requisitos**:
- [ ] CRUD básico: Create, Read (uno y lista), Update, Delete
- [ ] Métodos específicos de negocio (get_by_sku, get_all_recent, etc.)
- [ ] Manejo de transacciones (commit, rollback)
- [ ] Tests para cada método

**Puntaje**: ✅ Task 4 completa cuando todos los repos funcionan + testean

---

### **TAREA 5: Integración con DemandPredictor**

**Ubicación**: Modificar `modulo_analitico/predictor.py`

**Agregar método**:
```python
def save_predictions_to_db(self, predictions_df: pd.DataFrame, db_session):
    """Guardar predicciones en BD después de predict()."""
    from logica_negocio.database.repositories import PredictionRepository
    
    repo = PredictionRepository(db_session)
    
    for _, row in predictions_df.iterrows():
        pred_schema = PredictionCreate(
            sku_id=row['sku_id'],
            week_start=row['week_start'],
            predicted_demand=row['predicted_demand'],
            confidence_level=row['confidence_level'],
            lower_bound=row['lower_bound'],
            upper_bound=row['upper_bound'],
            mape=row['mape']
        )
        repo.create(pred_schema)
```

**Modificar método**:
```python
def train(self, db_session=None):
    """Entrenar y guardar en BD si db_session se proporciona."""
    results = self._train_internal()
    
    if db_session:
        # Guardar fold metrics
        eval_repo = EvaluationFoldRepository(db_session)
        for fold, metrics in results['fold_metrics'].items():
            eval_repo.create(EvaluationFoldCreate(
                fold_number=fold,
                mape=metrics['mape'],
                mae=metrics['mae'],
                bias=metrics['bias']
            ))
```

**Requisitos**:
- [ ] DemandPredictor acepta db_session (opcional)
- [ ] No rompe flujos existentes (mantiene backward compatibility)
- [ ] Tests que verifican guardado en BD

**Puntaje**: ✅ Task 5 completa cuando DemandPredictor persiste predicciones

---

### **TAREA 6: Unit Tests para Repositories**

**Ubicación**: `logica_negocio/tests/` (nuevo directorio)

**Crear**: `test_prediction_repository.py`, etc.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logica_negocio.database.models import Base
from logica_negocio.database.repositories.prediction_repository import PredictionRepository
from logica_negocio.database.schemas.prediction import PredictionCreate
from datetime import date

@pytest.fixture
def test_db():
    """Crear BD en memoria para tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_prediction(test_db):
    repo = PredictionRepository(test_db)
    
    pred = PredictionCreate(
        sku_id=1,
        week_start=date(2026, 1, 1),
        predicted_demand=100.0,
        confidence_level=0.9,
        lower_bound=95.0,
        upper_bound=105.0,
        mape=5.0
    )
    
    result = repo.create(pred)
    
    assert result.id is not None
    assert result.sku_id == 1
    assert result.predicted_demand == 100.0
```

**Requisitos**:
- [ ] Mínimo 5 tests por repository
- [ ] Tests CRUD completo
- [ ] Tests de casos edge (duplicate keys, foreign key errors)
- [ ] 100% passing

**Puntaje**: ✅ Task 6 completa cuando 20+ tests passing

---

## 📊 CHECKLIST FINAL FASE 3

```bash
# 1. Schema en Supabase
[ ] CREATE TABLE sku
[ ] CREATE TABLE prediction
[ ] CREATE TABLE evaluation_fold
[ ] CREATE TABLE model_version

# 2. SQLAlchemy Models
[ ] models/sku.py creado
[ ] models/prediction.py creado
[ ] models/evaluation_fold.py creado
[ ] models/model_version.py creado
[ ] Base.metadata.create_all() funciona

# 3. Pydantic Schemas
[ ] schemas/sku.py creado (Read/Create)
[ ] schemas/prediction.py creado
[ ] schemas/evaluation_fold.py creado
[ ] schemas/model_version.py creado
[ ] Validaciones funcionar

# 4. Repositories
[ ] sku_repository.py con CRUD
[ ] prediction_repository.py con bulk_create()
[ ] evaluation_fold_repository.py
[ ] model_version_repository.py
[ ] Todos funcionan

# 5. Integración
[ ] DemandPredictor.save_predictions_to_db() existe
[ ] DemandPredictor.train() guarda en BD
[ ] No rompe tests existentes (29/29 aún PASS)

# 6. Tests
[ ] test_prediction_repository.py (5+ tests)
[ ] test_sku_repository.py (5+ tests)
[ ] test_evaluation_fold_repository.py (5+ tests)
[ ] Total: 20+ tests nuevos, todos PASS

# 7. Documentación
[ ] README actualizado con Fase 3
[ ] BITÁCORA listar tareas completadas
[ ] Docstrings en todas las funciones nuevas

# 8. Git
[ ] Commit: "Fase 3: Implement Repository Pattern + Supabase integration"
[ ] Branch: feature/fase3-modulo-datos limpio
[ ] Tests: pytest logica_negocio/tests/ -v (20+ PASS)
```

---

## ⚠️ ANTI-PATRONES A EVITAR EN FASE 3

```python
# ❌ MAL: SQL raw
session.execute("INSERT INTO prediction ...")

# ✅ CORRECTO: Repository
repo = PredictionRepository(session)
repo.create(PredictionCreate(...))

# ❌ MAL: Hardcoding IDs
prediction.sku_id = 123  # ← Hardcoded

# ✅ CORRECTO: Desde lookup
sku = sku_repo.get_by_code("SKU-001")
prediction.sku_id = sku.id

# ❌ MAL: No manejar excepciones
session.add(obj)
session.commit()  # ← Puede fallar

# ✅ CORRECTO: Try-except
try:
    session.add(obj)
    session.commit()
except IntegrityError:
    session.rollback()
    raise ValueError("Duplicate key")
```

---

## 🔗 CONEXIÓN CON FASE 4

En Fase 4 (REST API), estas Repositories se usarán así:

```python
# main.py (FastAPI)
from fastapi import FastAPI, Depends
from logica_negocio.database.repositories import PredictionRepository

@app.get("/predictions/{sku_id}")
def get_predictions(sku_id: int, db: Session = Depends(get_db)):
    repo = PredictionRepository(db)
    return repo.get_all_by_sku(sku_id)
```

**Por eso Fase 3 es crítica**: Define interface que FastAPI consumirá.

---

## 📚 REFERENCIAS

- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- Pydantic v2: https://docs.pydantic.dev/
- Repository Pattern: Clean Code architecture
- Supabase SQL: https://supabase.com/docs/guides/database

---

**Fase 3 inicio**: Después de verificar Fase 2 ✅  
**Fase 3 objetivo**: 6 tareas, 20+ tests, 100% PASS  
**Fase 3 salida**: Datos persistidos en Supabase, ready para Fase 4
