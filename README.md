# DEMAND-24 — Sistema Inteligente de Predicción de Demanda

> **MiniMarket La 24 S.A.S.** — Prototipo funcional de predicción de demanda semanal por SKU con modelo de Machine Learning, alertas de quiebre de stock y dashboard de visualización.

## 🏗️ Arquitectura

El sistema sigue una **arquitectura hexagonal (Ports & Adapters)** con tres módulos principales:

| Módulo | Responsabilidad | Tecnología |
|--------|----------------|-----------|
| **Módulo de Datos** | ETL, validación, repositorios | Python + SQLAlchemy + Pandas |
| **Módulo Analítico** | Entrenamiento, predicción, evaluación | scikit-learn + XGBoost + MLflow |
| **Módulo de Presentación** | API REST + Dashboard web | FastAPI + React.js + Recharts |

**Base de datos**: [Supabase](https://supabase.com) (PostgreSQL gestionado)  
**Dataset de entrenamiento**: [Store Sales - Corporación Favorita](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) (Kaggle)

## 📁 Estructura del Proyecto

```
demand-24/
├── backend/
│   ├── api/                  # FastAPI routers
│   ├── auth/                 # Autenticación (Supabase Auth)
│   ├── etl/                  # Pipeline ETL
│   ├── ml_engine/            # Motor de Machine Learning
│   ├── alert_engine/         # Motor de alertas
│   ├── models/               # SQLAlchemy ORM
│   ├── schemas/              # Pydantic DTOs
│   ├── repositories/         # Repository pattern
│   ├── config/               # Configuración centralizada
│   └── tests/                # Pruebas unitarias e integración
├── frontend/                 # React + Vite + Recharts
├── data/                     # Datasets (NO versionado)
│   └── raw/                  # CSVs de Kaggle
├── notebooks/                # Jupyter notebooks (EDA)
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (para despliegue)

### Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/AzTTeK/MiniMarket24.git
cd MiniMarket24

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# 3. Crear entorno virtual de Python
python -m venv venv
venv\Scripts\activate  # Windows

# 4. Instalar dependencias del backend
pip install -r backend/requirements.txt

# 5. Colocar dataset de Kaggle en data/raw/
# Descargar desde: https://www.kaggle.com/competitions/store-sales-time-series-forecasting
```

## 👥 Equipo

- Mateo Reyes – T00077079
- Elías José Blanco Gil – T00078817  
- Sebastian Valencia Montesino – T00078248
- Jose Pereira Acuña – T00079768
- Fabián Corpas Castro – T00064976

## 📄 Licencia

Proyecto académico — Universidad · Ingeniería de Software · 2026