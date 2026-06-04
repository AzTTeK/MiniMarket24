<div align="center">

# DEMAND-24
### Sistema Inteligente de Predicción de Demanda
**MiniMarket La 24 S.A.S.**

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=coverage)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1+-FF6600?style=flat-square)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)

</div>

---

## Descripcion

DEMAND-24 es un sistema de predicción de demanda para MiniMarket La 24 S.A.S. Combina un modelo de Machine Learning (XGBoost) con una API REST y un dashboard interactivo para que los responsables de inventario anticipen cuánto stock necesitarán semana a semana, reduciendo el desabastecimiento y el sobreinventario.

---

## Funcionalidades Principales

| Funcionalidad | Descripcion |
|:---|:---|
| Prediccion de demanda | Predice ventas semanales por familia de productos (1-4 semanas) con intervalos de confianza al 90% |
| Alertas de stock | Genera alertas automaticas cuando el stock proyectado cae por debajo del umbral configurado |
| Dashboard analitico | Visualiza tendencias, predicciones y KPIs en tiempo real |
| Entrenamiento de modelo | Permite re-entrenar el modelo desde la UI o via API, con validacion walk-forward |
| Gestion de SKUs | CRUD completo de productos con persistencia en PostgreSQL |
| Autenticacion | Login y registro integrado con Supabase Auth |

---

## Arquitectura

El proyecto sigue una arquitectura de 3 capas con separacion estricta de responsabilidades:

```
modulo_analitico/        -- Motor de ML (XGBoost, feature engineering, evaluacion)
logica_negocio/          -- Backend REST (FastAPI, repositorios, DTOs Pydantic)
frontend/                -- Dashboard (React 19 + Vite, Recharts, Framer Motion)
```

**Flujo de datos:**

```
CSV Raw Data --> DataLoader --> DataAggregator (daily -> weekly)
             --> FeatureBuilder --> XGBoostDemandModel --> DemandPredictor
             --> FastAPI (/api/v1) --> React Dashboard
```

---

## Tecnologias

**Backend / ML:** Python 3.11, FastAPI, XGBoost, Scikit-learn, Pandas, NumPy, Statsmodels, MLflow, Pydantic, SQLAlchemy

**Base de datos:** Supabase (PostgreSQL), SQLite (desarrollo local)

**Frontend:** React 19, Vite, Recharts, Framer Motion, Axios

**DevOps:** GitHub Actions, SonarCloud, Pytest, Ruff

---

## Despliegue

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- Cuenta en [Supabase](https://supabase.com)
- Dataset de [Kaggle Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)

### Instalacion

```bash
# 1. Clonar el repositorio
git clone https://github.com/AzTTeK/MiniMarket24.git
cd MiniMarket24

# 2. Entorno virtual Python
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Dependencias del backend
pip install -e ".[dev]"

# 4. Colocar los CSVs del dataset en data/raw/
#    (train.csv, stores.csv, holidays_events.csv, oil.csv)
```

### Variables de entorno

Crea un archivo `.env` en la raiz del proyecto:

```env
SUPABASE_URL=https://<tu-proyecto>.supabase.co
SUPABASE_ANON_KEY=<tu-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<tu-service-role-key>
DATABASE_URL=postgresql://postgres:<password>@db.<host>.supabase.co:5432/postgres
APP_ENV=development
APP_PORT=8000
MAPE_LOW_CONFIDENCE_THRESHOLD=25.0
MIN_WEEKS_HISTORY=4
```

### Ejecucion

```bash
# Backend (FastAPI)
uvicorn logica_negocio.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs

# Frontend (React)
cd frontend
npm install
npm run dev
# Dashboard: http://localhost:5173

# Tests
pytest
```

---

## API REST

| Metodo | Endpoint | Descripcion |
|:---:|:---|:---|
| GET | `/api/v1/health` | Estado del sistema |
| POST | `/api/v1/auth/login` | Inicio de sesion |
| GET | `/api/v1/skus` | Listar productos |
| POST | `/api/v1/skus` | Crear producto |
| GET | `/api/v1/predictions` | Consultar predicciones |
| POST | `/api/v1/training` | Iniciar entrenamiento |
| GET | `/api/v1/alerts` | Listar alertas activas |
| GET | `/api/v1/dashboard` | Metricas del panel |

---

## Calidad de Codigo

El repositorio ejecuta un pipeline de CI en GitHub Actions en cada push a `main`:

1. Instalar dependencias
2. Ejecutar suite de tests con Pytest (50+ casos de prueba)
3. Generar reporte de cobertura (`coverage.xml`)
4. Analisis estatico con SonarCloud (calidad, seguridad, duplicaciones)

**Criterio de aceptacion CA-01:** MAPE <= 25% en validacion walk-forward sobre el horizonte de prediccion.

---

## Equipo

| Nombre | ID |
|:---|:---|
| **Elias Jose Blanco Gil** | T00078817 |
| Mateo Reyes | T00077079 |
| Sebastian Valencia Montesino | T00078248 |

---

<div align="center">

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)

</div>
