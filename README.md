## HAY QUE ACTUALIZARLO

## Arquitectura Modular

El sistema está diseñado bajo una arquitectura modular estricta, dividida en tres pilares fundamentales que garantizan el desacoplamiento y la escalabilidad del prototipo:

| Módulo | Responsabilidad | Tecnología |
|--------|----------------|-----------|
| **Módulo Analítico** | Corazón del sistema: modelado de IA, entrenamiento y generación de predicciones. | Python + statsmodels + XGBoost |
| **Lógica de Negocio** | Gestión de datos, motor de alertas, autenticación y reglas de negocio. | FastAPI + Supabase |
| **Visualización** | Interfaz de usuario dinámica para la toma de decisiones basada en datos. | React.js + Recharts |

**Base de datos**: [Supabase](https://supabase.com) (PostgreSQL gestionado)  
**Dataset de entrenamiento**: [Store Sales - Corporación Favorita](https://www.kaggle.com/competitions/store-sales-time-series-forecasting) (Kaggle)

## Estructura del Proyecto

```
demand-24/
├── modulo_analitico/         # Procesamiento de IA y ML 
├── logica_negocio/           # Backend y API´s
├── visualizacion/            # Frontend y Dashboard Web
├── data/                     # Datasets descargados 
│   └── raw/                  # CSVs originales de Kaggle
├── notebooks/                # Jupyter notebooks para experimentación
├── .env.example
├── .gitignore
└── README.md
```


## Inicio Rápido

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

## Equipo

- Elías José Blanco Gil – T00078817  
- Mateo Reyes – T00077079
- Sebastian Valencia Montesino – T00078248
- Jose Pereira Acuña – T00079768
- Fabián Corpas Castro – T00064976
