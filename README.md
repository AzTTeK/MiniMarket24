<div align="center">

<img src="https://img.shields.io/badge/DEMAND--24-Sistema%20Inteligente%20de%20Predicción-6366f1?style=for-the-badge&logo=robot&logoColor=white" alt="DEMAND-24"/>

# 🛒 DEMAND-24
### Sistema Inteligente de Predicción de Demanda
**MiniMarket La 24 S.A.S.**

*Solución modular para la gestión de inventarios y predicción de demanda basada en Inteligencia Artificial*

---

[![Build Status](https://github.com/AzTTeK/MiniMarket24/actions/workflows/build.yml/badge.svg)](https://github.com/AzTTeK/MiniMarket24/actions/workflows/build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=coverage)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=bugs)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=AzTTeK_MiniMarket24&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1+-FF6600?style=flat-square&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>

---

## 📌 ¿Qué es DEMAND-24?

**DEMAND-24** es un sistema de predicción de demanda de inventario diseñado para **MiniMarket La 24 S.A.S.**, una pequeña y mediana empresa de retail. El sistema combina un motor de Machine Learning (ML) con una API REST y un dashboard interactivo para que los responsables de inventario puedan anticipar cuánto stock necesitarán semana a semana, reduciendo tanto el desabastecimiento como el sobreinventario.

> **Problema que resuelve:** Los minimarkets gestionan decenas de familias de productos (SKUs) sin herramientas de análisis predictivo, lo que genera pérdidas por exceso de inventario perecedero o ventas perdidas por falta de stock. DEMAND-24 automatiza la predicción con IA para que las decisiones de compra sean basadas en datos.

---

## 🎯 ¿Para qué sirve?

| Funcionalidad | Descripción |
|:---|:---|
| 📈 **Predicción de demanda** | Predice la demanda semanal por familia de productos (hasta 4 semanas adelante) con intervalos de confianza al 90% |
| 🚨 **Alertas de stock** | Genera alertas automáticas cuando el stock proyectado cae por debajo del umbral mínimo configurado |
| 📊 **Dashboard analítico** | Visualiza tendencias, predicciones, KPIs y el estado del inventario en tiempo real |
| 🤖 **Motor de ML auto-entrenable** | Permite re-entrenar el modelo desde la UI o vía API, con validación walk-forward para evitar data leakage |
| 🔐 **Autenticación** | Sistema de login/registro integrado con Supabase Auth |
| 📦 **Gestión de SKUs** | CRUD completo de unidades de inventario con persistencia en PostgreSQL |

---

## ⚙️ ¿Cómo funciona?

El sistema sigue un flujo de datos claro y desacoplado:

```
                ┌──────────────────────────────────────────────────────┐
                │               FLUJO DE PREDICCIÓN                   │
                └──────────────────────────────────────────────────────┘

  📂 CSV Raw Data              🧠 Módulo Analítico           💾 Supabase / SQLite
  (Kaggle Dataset)   ──────►   DataLoader                  ◄──────────────────────
                               DataAggregator (daily→weekly)         ▲
                               FeatureBuilder (lags, rolling, etc)   │
                               XGBoostDemandModel                    │
                               WalkForwardEvaluator                  │
                                        │                            │
                                        ▼                            │
                             ⚡ DemandPredictor (API Pública)         │
                                        │                            │
                                        ▼                            │
                              🌐 FastAPI Backend ──────────────────────
                              /api/v1/predictions
                              /api/v1/alerts
                              /api/v1/skus
                              /api/v1/training
                                        │
                                        ▼
                              🖥️ React Dashboard
                              DemandChart | AlertPanel
                              PredictionTable | KPICard
```

### Pipeline de ML paso a paso

1. **Carga de datos** (`DataLoader`): Ingiere los CSV de ventas históricas, tiendas, feriados y precio del petróleo.
2. **Agregación** (`DataAggregator`): Convierte ventas diarias en registros semanales agrupados por familia de producto y tienda.
3. **Ingeniería de features** (`FeatureBuilder`): Construye más de 30 variables predictivas: lags temporales, estadísticas rolling, indicadores de feriados, estacionalidad y variables de promociones.
4. **Entrenamiento** (`ModelTrainer` + `XGBoostDemandModel`): Entrena un modelo XGBoost con **TimeSeriesSplit Cross-Validation** (5 folds) para garantizar que no haya data leakage entre entrenamiento y validación.
5. **Evaluación** (`WalkForwardEvaluator`): Aplica validación walk-forward sobre el horizonte de predicción y calcula MAPE, MAE y Bias por SKU.
6. **Predicción** (`DemandPredictor.predict()`): Genera predicciones para 1 a 4 semanas hacia adelante con intervalos de confianza al 90%.
7. **Persistencia y API**: Las predicciones se guardan en PostgreSQL (Supabase) y se exponen vía FastAPI al dashboard React.

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una **arquitectura modular de 3 capas** con separación estricta de responsabilidades:

```
MiniMarket24/
│
├── 🧠 modulo_analitico/           # Motor de Machine Learning (ML Engine)
│   ├── config/                    # Configuración del pipeline de ML
│   ├── data_adapter/              # Carga, agregación y feature engineering
│   │   ├── loader.py              # DataLoader — lectura de CSVs
│   │   ├── aggregator.py          # DataAggregator — daily → weekly
│   │   └── feature_builder.py    # FeatureBuilder — construcción de variables
│   ├── models/                    # Modelos de ML
│   │   ├── xgboost_model.py       # XGBoostDemandModel con CI al 90%
│   │   └── metrics.py             # Criterios de aceptación (CA-01: MAPE ≤ 25%)
│   ├── training/                  # Entrenamiento y evaluación
│   │   ├── trainer.py             # ModelTrainer con TimeSeriesSplit CV
│   │   └── evaluator.py          # WalkForwardEvaluator
│   ├── wrappers/                  # Wrappers de librerías externas (anti-acoplamiento)
│   ├── predictor.py               # 🚪 API pública del módulo analítico
│   └── tests/                     # Suite de tests del motor ML
│
├── ⚡ logica_negocio/              # Backend REST API (FastAPI)
│   ├── api/                       # Endpoints REST
│   │   ├── routes_health.py       # GET /health — Estado del sistema
│   │   ├── routes_auth.py         # POST /auth — Autenticación
│   │   ├── routes_skus.py         # CRUD /skus — Gestión de productos
│   │   ├── routes_predictions.py  # GET /predictions — Consulta de predicciones
│   │   ├── routes_training.py     # POST /training — Disparo de entrenamiento
│   │   ├── routes_alerts.py       # GET/PUT /alerts — Alertas de stock
│   │   └── routes_dashboard.py    # GET /dashboard — Métricas del panel
│   ├── auth/                      # Módulo de autenticación (Supabase Auth)
│   ├── config/
│   │   └── settings.py            # Configuración centralizada (vía .env)
│   ├── core/                      # Utilidades transversales del backend
│   ├── database/
│   │   ├── models/                # Modelos SQLAlchemy (ORM)
│   │   ├── repositories/          # Repository Pattern (CRUD desacoplado)
│   │   └── schemas/               # Pydantic DTOs (contratos de API)
│   ├── tests/                     # 13 archivos de test — 50+ casos
│   └── main.py                    # Punto de entrada FastAPI
│
├── 🖥️ frontend/                   # Dashboard React (Vite)
│   └── src/
│       ├── components/
│       │   ├── DemandChart.jsx    # Gráfico de predicción con Recharts
│       │   ├── AlertPanel.jsx     # Panel de alertas de stock
│       │   ├── PredictionTable.jsx # Tabla de predicciones
│       │   ├── KPICard.jsx        # Tarjetas de métricas clave
│       │   └── Sidebar.jsx        # Navegación lateral
│       ├── services/              # Capa de acceso a la API (Axios)
│       ├── App.jsx                # Componente raíz y enrutamiento
│       └── index.css              # Sistema de diseño con tokens CSS
│
├── 📊 data/                       # Datasets (no versionados)
│   └── raw/                       # CSVs de Kaggle Store Sales
├── 📓 notebooks/                  # Análisis exploratorio (Jupyter)
├── 📁 Documents/                  # SRS, Arquitectura, ERD
├── .env                           # Variables de entorno (no versionado)
├── pyproject.toml                 # Configuración del proyecto Python
├── sonar-project.properties       # Configuración SonarCloud
└── .github/workflows/build.yml    # CI/CD — GitHub Actions + SonarCloud
```

---

## 🛠️ Tecnologías Utilizadas

### Backend & Machine Learning

| Tecnología | Versión | Uso |
|:---|:---|:---|
| **Python** | 3.11+ | Lenguaje principal del backend y ML |
| **FastAPI** | ≥ 0.115 | API REST asíncrona con documentación OpenAPI automática |
| **Uvicorn** | ≥ 0.30 | Servidor ASGI de alto rendimiento |
| **XGBoost** | ≥ 2.1 | Modelo de predicción por gradient boosting |
| **Scikit-learn** | ≥ 1.5 | TimeSeriesSplit, métricas de evaluación |
| **Pandas** | ≥ 2.2 | Manipulación y transformación de datos |
| **NumPy** | ≥ 1.26 | Operaciones numéricas vectorizadas |
| **Statsmodels** | ≥ 0.14 | Análisis estadístico e intervalos de confianza |
| **MLflow** | ≥ 2.15 | Tracking de experimentos y versiones de modelos |
| **Pydantic** | ≥ 2.8 | Validación de datos y contratos de API (DTOs) |
| **SQLAlchemy** | ≥ 2.0 | ORM para acceso a base de datos |
| **python-dotenv** | ≥ 1.0 | Gestión de variables de entorno |
| **httpx** | ≥ 0.27 | Cliente HTTP asíncrono |
| **psycopg2-binary** | ≥ 2.9 | Driver PostgreSQL |

### Base de Datos & Infraestructura

| Tecnología | Uso |
|:---|:---|
| **Supabase** | PostgreSQL gestionado, autenticación y storage |
| **PostgreSQL** | Base de datos relacional en producción |
| **SQLite** | Base de datos local para desarrollo y testing |

### Frontend

| Tecnología | Versión | Uso |
|:---|:---|:---|
| **React** | 19 | Framework de UI basado en componentes |
| **Vite** | ≥ 8 | Build tool y servidor de desarrollo ultrarrápido |
| **Recharts** | ≥ 3.8 | Gráficos de predicción y tendencias |
| **Framer Motion** | ≥ 12 | Animaciones y transiciones de UI |
| **Lucide React** | ≥ 1.14 | Iconografía consistente |
| **Axios** | ≥ 1.16 | Cliente HTTP para consumo de la API |
| **@supabase/supabase-js** | ≥ 2 | Cliente Supabase para autenticación en el frontend |

### DevOps & Calidad

| Tecnología | Uso |
|:---|:---|
| **GitHub Actions** | CI/CD — ejecuta tests y análisis en cada push a `main` |
| **SonarCloud** | Análisis estático de código, cobertura y seguridad |
| **Pytest** | Framework de testing (50+ casos de prueba) |
| **pytest-cov** | Reporte de cobertura de código |
| **pytest-asyncio** | Testing de endpoints asíncronos FastAPI |
| **Ruff** | Linter y formatter de Python (reemplaza flake8 + isort) |

---

## 🚀 Despliegue: Guía Paso a Paso

### Prerrequisitos

- **Python 3.11+** — [descargar](https://python.org/downloads)
- **Node.js 18+** — [descargar](https://nodejs.org)
- **Git** — [descargar](https://git-scm.com)
- **Cuenta en Supabase** — [registrarse gratis](https://supabase.com)
- **Dataset de Kaggle** — [Store Sales Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)

---

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/AzTTeK/MiniMarket24.git
cd MiniMarket24
```

### 2️⃣ Configurar el entorno virtual de Python

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate

# Activar en Linux/macOS
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias del backend

```bash
# Instalación de producción
pip install -e .

# Instalación con dependencias de desarrollo (pytest, ruff, jupyter, etc.)
pip install -e ".[dev]"
```

### 4️⃣ Configurar las variables de entorno

Crea el archivo `.env` en la raíz del proyecto a partir del siguiente template:

```env
# ── Supabase ─────────────────────────────────────────────────
SUPABASE_URL=https://<tu-proyecto>.supabase.co
SUPABASE_ANON_KEY=<tu-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<tu-service-role-key>

# ── Base de datos (conexión directa a PostgreSQL) ─────────────
DATABASE_URL=postgresql://postgres:<password>@db.<host>.supabase.co:5432/postgres

# ── MLflow ───────────────────────────────────────────────────
MLFLOW_TRACKING_URI=http://localhost:5000

# ── Configuración del piloto ─────────────────────────────────
PILOT_SKU_IDS=GROCERY I,BEVERAGES,DAIRY
MIN_WEEKS_HISTORY=4
MAPE_LOW_CONFIDENCE_THRESHOLD=25.0
ETL_SCHEDULE_CRON=0 5 * * 1

# ── Aplicación ───────────────────────────────────────────────
APP_ENV=development
APP_DEBUG=true
APP_PORT=8000
```

> ⚠️ **NUNCA** subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

### 5️⃣ Cargar el dataset

Descarga el dataset desde [Kaggle Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data) y coloca los archivos en `data/raw/`:

```
data/
└── raw/
    ├── train.csv
    ├── stores.csv
    ├── holidays_events.csv
    └── oil.csv
```

### 6️⃣ Ejecutar el backend (FastAPI)

```bash
uvicorn logica_negocio.main:app --reload --port 8000
```

La API estará disponible en:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/api/v1/health

### 7️⃣ Ejecutar el frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

El dashboard estará disponible en: **http://localhost:5173**

### 8️⃣ (Opcional) Ejecutar la suite de tests

```bash
# Desde la raíz del proyecto
pytest

# Con reporte de cobertura detallado
pytest --cov=logica_negocio --cov=modulo_analitico --cov-report=term-missing
```

---

## 🔌 API REST — Endpoints Disponibles

| Método | Endpoint | Descripción |
|:---:|:---|:---|
| `GET` | `/api/v1/health` | Estado del sistema |
| `POST` | `/api/v1/auth/login` | Inicio de sesión |
| `POST` | `/api/v1/auth/register` | Registro de usuario |
| `GET` | `/api/v1/skus` | Listar todos los SKUs |
| `POST` | `/api/v1/skus` | Crear un nuevo SKU |
| `GET` | `/api/v1/predictions` | Consultar predicciones activas |
| `POST` | `/api/v1/training` | Iniciar entrenamiento del modelo |
| `GET` | `/api/v1/alerts` | Listar alertas de stock activas |
| `PUT` | `/api/v1/alerts/{id}` | Actualizar estado de una alerta |
| `GET` | `/api/v1/dashboard` | Métricas resumen del panel |

> Consulta la documentación interactiva completa en `/docs` (Swagger UI) mientras el servidor está corriendo.

---

## 🧠 Módulo de ML — Uso Programático

```python
from modulo_analitico.predictor import DemandPredictor

# Inicializar predictor (carga config desde .env automáticamente)
predictor = DemandPredictor()

# Pipeline completo en 4 líneas
predictor.load_data()
predictor.prepare_data()
metrics = predictor.train(use_cross_validation=True)
predictions = predictor.predict(weeks_ahead=4, with_confidence_intervals=True)

# Ver métricas
print(f"MAPE promedio: {metrics['mape_mean']:.2f}% ± {metrics['mape_std']:.2f}%")

# Ver las primeras predicciones
print(predictions.head())
# week_start  store_nbr  family      prediction  ci_lower  ci_upper  confidence_level
# 2026-01-05          1  GROCERY I     1250.45     987.32    1513.58          HIGH
```

---

## 📊 Criterios de Aceptación (CA-01)

El modelo debe cumplir el criterio de aceptación CA-01 definido en el SRS:

| Métrica | Umbral de Aceptación |
|:---|:---|
| **MAPE (Error Porcentual Absoluto Medio)** | ≤ 25% en validación walk-forward |
| **Nivel de confianza** | `HIGH` si MAPE ≤ 25%, `LOW` en caso contrario |
| **Semanas de predicción** | 1 a 4 semanas hacia adelante |
| **Intervalo de confianza** | 90% (percentil 5 - percentil 95) |
| **Historial mínimo requerido** | 4 semanas por SKU (configurable en `MIN_WEEKS_HISTORY`) |

---

## 📁 Documentación Técnica

En la carpeta [`Documents/`](./Documents/) encontrarás:

| Documento | Contenido |
|:---|:---|
| **SRS** | Especificación de Requerimientos del Sistema (Funcionales y No Funcionales) |
| **Arquitectura Modular** | Diseño de alto nivel y diagramas de componentes |
| **Bitácora de Desarrollo** | Historial de decisiones técnicas y cambios |
| **Decisiones Arquitectónicas** | ADRs (Architecture Decision Records) |
| **Modelado de Aplicación** | Diagramas de clases y flujos |

---

## 🔄 Integración Continua (CI/CD)

El repositorio cuenta con un pipeline de GitHub Actions (`.github/workflows/build.yml`) que se ejecuta automáticamente en cada `push` a `main` o apertura de Pull Request:

```
Push / PR → main
    ↓
[GitHub Actions]
    1. Checkout del código
    2. Configurar Python 3.11
    3. Instalar dependencias (pip install .[dev])
    4. Ejecutar pytest + reporte de cobertura (coverage.xml)
    5. Análisis SonarCloud (calidad, seguridad, cobertura)
```

---

## 👥 Equipo de Desarrollo

| Nombre | ID |
|:---|:---|
| **Elías José Blanco Gil** *(Autor Principal)* | T00078817 |
| Mateo Reyes | T00077079 |
| Sebastian Valencia Montesino | T00078248 |
| Jose Pereira Acuña | T00079768 |
| Fabián Corpas Castro | T00064976 |

---

## 📜 Licencia

Este proyecto es de uso académico y educativo para **MiniMarket La 24 S.A.S.** — Todos los derechos reservados por los autores.

---

<div align="center">

**Desarrollado con ❤️ por el equipo AzTTeK**

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=AzTTeK_MiniMarket24)

</div>
