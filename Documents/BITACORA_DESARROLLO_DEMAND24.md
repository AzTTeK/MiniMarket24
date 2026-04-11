# DEMAND-24 — Bitácora de Desarrollo

**Proyecto**: Sistema Inteligente de Predicción de Demanda para MiniMarket La 24 S.A.S.  
**Equipo**: Mateo Reyes, Elías José Blanco Gil, Sebastian Valencia Montesino, Jose Pereira Acuña, Fabián Corpas Castro  
**Inicio del desarrollo**: 11 de abril de 2026 

---

## Fase 1 — Fundación del Proyecto

### 11 de abril de 2026 — Sesión 1: Planificación y Setup Inicial

**¿Qué se hizo?**

Se realizó el análisis completo de toda la documentación existente del proyecto (SRS v2.0, Arquitectura Modular v1.0, Caso de Negocio, Mockup del Dashboard) para definir el plan de inicio del desarrollo.

**Decisiones técnicas tomadas:**

1. **Dataset de entrenamiento**: Se seleccionó el dataset **"Store Sales - Time Series Forecasting"** de **Corporación Favorita** (Kaggle). Este dataset contiene datos de ventas diarias de un retailer de abarrotes ecuatoriano con múltiples tiendas y familias de productos, lo que lo hace ideal para simular el escenario multi-sucursal de MiniMarket La 24. Los datos diarios se agregarán a nivel semanal para alinearse con el ciclo de reposición del negocio.

2. **Arquitectura Modular**: Se ha decidido implementar una **Arquitectura Modular estricta** para cumplir al 100% con los entregables del caso práctico. El sistema se divide en tres pilares:
   - **Módulo Analítico**: Responsable exclusivo del procesamiento de datos de IA y generación de predicciones.
   - **Lógica de Negocio**: Centraliza las reglas, la gestión de alertas y la integración con Supabase.
   - **Visualización**: Dashboard web enfocado en la toma de decisiones.

3. **Base de Datos**: Se confirma el uso de **Supabase** como proveedor oficial, integrándolo directamente en el Módulo de Lógica de Negocio.

4. **Estrategia de desarrollo**: Se definió un roadmap de 6 fases:
   - Fase 1: Fundación del proyecto (estructura del repo, configuración del entorno)
   - Fase 2: Módulo Analítico / ML Engine (EDA, feature engineering, entrenamiento de modelos)
   - Fase 3: Módulo de Datos (esquema en Supabase, ETL, Repository Pattern)
   - Fase 4: REST API (FastAPI, DTOs Pydantic, Auth, Alert Engine)
   - Fase 5: Web Dashboard (React + Vite + Recharts)
   - Fase 6: Integración, Testing y Despliegue

5. **Control de versiones**: El equipo mantendrá un repositorio en GitHub con mensajes de commit descriptivos. 

**Stack tecnológico confirmado:**

| Componente | Tecnología |
|-----------|-----------|
| Backend API | FastAPI + Uvicorn |
| ML Engine | scikit-learn + XGBoost + statsmodels |
| ML Tracking | MLflow |
| Base de datos | Supabase (PostgreSQL gestionado) |
| ORM | SQLAlchemy |
| Frontend | React.js + Vite + Recharts |
| Auth | Supabase Auth (JWT integrado) |
| Deploy | Docker Compose + Nginx |

### 11 de abril de 2026 — Sesión 2: Reorganización Modular Estricta

**¿Qué se hizo?**

Se ejecutó la reestructuración física del repositorio para alinearse al 100% con los entregables del caso práctico:

1.  **Módulo Analítico**: Se creó la carpeta `modulo_analitico/` para contener de forma aislada toda la lógica de IA (Adaptador, Entrenamiento, Modelos y Predictor).
2.  **Lógica de Negocio**: Se creó la carpeta `logica_negocio/` que centraliza la API (FastAPI), la integración con Supabase y las reglas de negocio (Alertas).
3.  **Visualización**: Se preparó la carpeta `visualizacion/` para el dashboard en React.

**Cambios técnicos:**
- Actualización de `pyproject.toml` para soportar las nuevas rutas de módulos.
- Actualización de `README.md` con la nueva arquitectura modular de 3 pilares.
- Re-staged de todos los archivos para asegurar un primer commit limpio con la estructura definitiva.

**Próximos pasos:**
- Realizar el primer commit con la estructura modular confirmada.
- Iniciar el análisis de datos (EDA) en el Módulo Analítico.

---

*Este documento se actualizará al final de cada sesión de trabajo.*
