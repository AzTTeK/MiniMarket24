# DEMAND-24 — Bitácora de Desarrollo

**Proyecto**: Sistema Inteligente de Predicción de Demanda para MiniMarket La 24 S.A.S.  
**Equipo**: Mateo Reyes, Elías José Blanco Gil, Sebastian Valencia Montesino, Jose Pereira Acuña, Fabián Corpas Castro  
**Inicio del desarrollo**: 11 de abril de 2026  
**Repositorio**: *(pendiente de vincular)*

---

## Fase 1 — Fundación del Proyecto

### 11 de abril de 2026 — Sesión 1: Planificación y Setup Inicial

**¿Qué se hizo?**

Se realizó el análisis completo de toda la documentación existente del proyecto (SRS v2.0, Arquitectura Modular v1.0, Caso de Negocio, Mockup del Dashboard) para definir el plan de inicio del desarrollo.

**Decisiones técnicas tomadas:**

1. **Dataset de entrenamiento**: Se seleccionó el dataset **"Store Sales - Time Series Forecasting"** de **Corporación Favorita** (Kaggle). Este dataset contiene datos de ventas diarias de un retailer de abarrotes ecuatoriano con múltiples tiendas y familias de productos, lo que lo hace ideal para simular el escenario multi-sucursal de MiniMarket La 24. Los datos diarios se agregarán a nivel semanal para alinearse con el ciclo de reposición del negocio.

2. **Base de datos**: Se decidió usar **Supabase** (PostgreSQL gestionado en la nube) en lugar de PostgreSQL dockerizado localmente. Razones: simplifica la configuración del entorno de desarrollo, ofrece autenticación integrada (útil para el módulo Auth), y proporciona una API REST auto-generada. La integración con Supabase se realizará en fases posteriores; la Fase 2 (ML Engine) trabaja directamente con los archivos CSV del dataset.

3. **Scope del MVP**: Se decidió implementar **todos los 9 requerimientos funcionales** del SRS, priorizando RF-01 a RF-05 (ETL, validación de datos, predicción, alertas, visualización de tendencias) en las primeras iteraciones, y RF-06 a RF-09 (registro de venta real, reentrenamiento, ajuste manual, comparación entre sucursales) en iteraciones posteriores. El objetivo es entregar un sistema completo y funcional.

4. **Estrategia de desarrollo**: Se definió un roadmap de 6 fases:
   - Fase 1: Fundación del proyecto (estructura del repo, configuración del entorno)
   - Fase 2: Módulo Analítico / ML Engine (EDA, feature engineering, entrenamiento de modelos)
   - Fase 3: Módulo de Datos (esquema en Supabase, ETL, Repository Pattern)
   - Fase 4: REST API (FastAPI, DTOs Pydantic, Auth, Alert Engine)
   - Fase 5: Web Dashboard (React + Vite + Recharts)
   - Fase 6: Integración, Testing y Despliegue

5. **Control de versiones**: El equipo mantendrá un repositorio en GitHub con mensajes de commit descriptivos. Los cambios se subirán de forma atómica y verificada.

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

**Próximos pasos:**
- Configurar la estructura de carpetas del repositorio
- Descargar y colocar el dataset de Kaggle en `data/raw/`
- Iniciar la Fase 2: Análisis Exploratorio de Datos (EDA)

---

*Este documento se actualizará al final de cada sesión de trabajo.*
