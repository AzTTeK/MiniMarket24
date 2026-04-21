# DEMAND-24 - Sistema Inteligente de Predicción de Demanda

*Solución modular para el manejo de inventarios y predicción de demanda basada en Inteligencia Artificial.*

---

##  Estado del Proyecto

| Fase | Tarea | Estado |
| :--- | :--- | :--- |
| **1** | **Fundación del Proyecto** |  Completada |
| **2** | **Módulo Analítico (ML Engine)** |  Completada |
| **3** | **Módulo de Datos (Persistencia / Supabase)** |  Completada |
| **4** | **Orquestación & API (FastAPI)** |  En proceso |
| **5** | **Dashboard Visual (React)** |  Pendiente |
| **6** | **Integración & Despliegue** |  Pendiente |

---

##  Arquitectura Modular

El sistema se divide en tres pilares fundamentales para garantizar el desacoplamiento y la escalabilidad del prototipo:

*   **Módulo Analítico (`modulo_analitico/`)**: Corazón del sistema. Modelado de IA con XGBoost, generación de predicciones semanalas e intervalos de confianza.
*   **Lógica de Negocio (`logica_negocio/`)**: Gestión de datos, repositorio centralizado, motor de alertas y API REST.
*   **Visualización (`visualizacion/`)**: Interfaz de usuario dinámica para la toma de decisiones basada en datos.

---

##  Estructura del Repositorio

```text
MiniMarket24/
├── modulo_analitico/      # ML Engine (Transformers, Aggregators, Models)
├── logica_negocio/        # Persistencia, Repositorios y Backend
│   ├── database/          # Modelos SQLAlchemy y Repository Pattern
│   └── tests/             # Suite de 50+ tests para la capa de datos
├── Documents/             # Documentación oficial (SRS, Arquitectura, ERD)
├── data/                  # Almacenamiento local de Datasets (vía .env)
├── notebooks/             # Análisis exploratorio y prototipado
├── .env                   # Variables de entorno (No versionado)
└── README.md
```

---

##  Inicio Rápido

### Prerrequisitos
- **Python 3.11+**
- **Node.js 18+**
- **Cuenta en Supabase** (PostgreSQL)

### Instalación
1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/AzTTeK/MiniMarket24.git
    cd MiniMarket24
    ```

2.  **Configurar entorno virtual:**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -e .
    ```

4.  **Configurar Datos:**
    Descarga el dataset de [Kaggle - Store Sales](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) y ubícalo en `data/raw/`.

---

##  Equipo de Desarrollo

- **Elías José Blanco Gil** – T00078817  
- **Mateo Reyes** – T00077079
- **Sebastian Valencia Montesino** – T00078248
- **Jose Pereira Acuña** – T00079768
- **Fabián Corpas Castro** – T00064976

---

##  Documentación
Para detalles técnicos sobre requerimientos, modelos de datos y decisiones arquitectónicas, consulta la carpeta [Documents/](file:///Documents/).
