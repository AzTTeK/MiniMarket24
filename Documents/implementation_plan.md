# DEMAND-24 — Plan de Inicio del Proyecto (Rectificado: Arquitectura Modular)

## Contexto

**Sistema**: Predicción Inteligente de Demanda para MiniMarket La 24 S.A.S.  
**Objetivo**: Prototipo funcional que cumpla estrictamente con los entregables del caso: **Módulo Analítico**, **Lógica de Negocio** y **Visualización**.

Ya cuentas con documentación sólida, priorizando el documento de **Entregables**:
- [Entregables](file:///c:/Users/users/Desktop/ELÍAS/Minimarket24/Documents/Caso%20y%20entregables%20Sistema%20Inteligente%20de%20Predicción%20de%20Demanda%20para%20Mini.pdf) — **Fuente de Verdad de la Arquitectura (Modular)**.
- [SRS_MINIMARKET_DETALLADO.pdf](file:///c:/Users/users/Desktop/ELÍAS/Minimarket24/Documents/SRS_MINIMARKET_DETALLADO.pdf) — Requerimientos detallados.
- [DEMAND24_Arquitectura_Modular.pdf](file:///c:/Users/users/Desktop/ELÍAS/Minimarket24/Documents/DEMAND24_Arquitectura_Modular.pdf) — Detalle de servicios y despliegue.

---

## User Review Required

> [!IMPORTANT]
> **Arqusitectura Modular (Rectificación)**: Siguiendo estrictamente los entregables, el proyecto se estructurará en tres módulos independientes:
> 1.  **Módulo Analítico**: Modelado de IA y procesamiento de datos (Kaggle).
> 2.  **Lógica de Negocio**: Backend con FastAPI integrado con Supabase para persistencia y reglas.
> 3.  **Visualización**: Dashboard web en React.
> 
> Se elimina el patrón hexagonal para evitar sobre-ingeniería y alinearse al 100% con la rúbrica del proyecto.

> [!IMPORTANT]
> **Base de datos**: Usaremos **Supabase** como proveedor oficial de base de datos. Esto simplifica la gestión del Módulo de Lógica de Negocio al proporcionar persistencia, autenticación y API en un solo lugar.

---

## Roadmap en 6 Fases (Adaptado a Arquitectura Modular)

### Fase 1: Recimentación Modular (Semana 1)
Reorganizar el repositorio para reflejar los tres pilares del proyecto.

| Actividad | Detalle |
|-----------|---------|
| Reestructurar carpetas | Crear `modulo_analitico/`, `logica_negocio/` y `visualizacion/` |
| Actualizar Docs | README, Bitácora y .gitignore alineados a la nueva arquitectura |
| Setup Base | .env con credenciales de Supabase |

---

### Fase 2: Módulo Analítico (Semana 2-3) ⭐ *INICIAR AQUÍ*

| Actividad | Detalle |
|-----------|---------|
| **EDA** | Análisis exploratorio del dataset de Corporación Favorita |
| **Adaptador** | Transformar Kaggle → Esquema de dominio de MiniMarket 24 |
| **Modelado** | XGBoost para predicción semanal con intervalos de confianza |
| **Evaluación** | Métricas MAPE, MAE y validación temporal |

```
modulo_analitico/
├── data_adapter/      # Adaptación dataset Kaggle
├── models/            # Versiones guardadas de modelos
├── training/          # Lógica de entrenamiento
└── predictor.py       # API interna de predicción
```

---

### Fase 3: Módulo de Lógica de Negocio (Semana 3-4)

| Actividad | Detalle |
|-----------|---------|
| **Integración Supabase** | Definición de tablas en Supabase y conexión FastAPI |
| **Reglas de Negocio** | Motor de alertas de quiebre de stock y thresholds |
| **API REST** | Endpoints para predicciones, alertas y gestión de productos |

```
logica_negocio/
├── api/               # FastAPI routers
├── auth/              # Supabase Auth integration
├── database/          # Conexión y Repositorios
└── config/            # Settings centralizadas
```

---

### Fase 4: Módulo de Visualización (Semana 5-6)

| Actividad | Detalle |
|-----------|---------|
| **Dashboard** | Visualización de KPIs y alertas |
| **Tendencias** | Gráficas dinámicas de Ventas Reales vs Proyección |
| **Gestión** | Vistas para Administradores y Gerencia |

```
visualizacion/         # React App
├── components/
├── pages/
└── services/          # API Clients
```

---

## Estructura del Repositorio (Modular Estricta)

```
demand-24/
├── modulo_analitico/         # Analítico
├── logica_negocio/           # Lógica de Negocio
├── visualizacion/            # Visualización
├── data/                     # Datos (NO versionado)
├── .env.example
├── .gitignore
└── README.md
```

## Stack Tecnológico

| Módulo | Tecnología | Justificación |
|------|-----------|---------------|
| **Analítico** | Python + XGBoost | Estándar de la industria para series temporales |
| **Lógica** | FastAPI + Supabase | Escalabilidad y rapidez de implementación |
| **Visualización** | React.js + Recharts | UX premium y visualización clara |

---

## Verification Plan

### Módulo Analítico
- MAPE ≤ 20% en conjunto de validación.
- Generación de intervalos de confianza al 90%.

### Módulo de Lógica de Negocio
- Endpoints documentados con Swagger (OpenAPI).
- Persistencia correcta de alertas en Supabase.

### Módulo de Visualización
- Contraste visual según mockup (semáforos de alerta).
- Responsive design para tablets de sucursal.
