"""
DEMAND-24 — FastAPI Application Entry Point

Punto de entrada principal del backend REST API.
Registra todos los routers, configura CORS y metadata OpenAPI.

Ejecución:
    uvicorn logica_negocio.main:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logica_negocio.api.routes_alerts import router as alerts_router
from logica_negocio.api.routes_health import router as health_router
from logica_negocio.api.routes_predictions import router as predictions_router
from logica_negocio.api.routes_skus import router as skus_router
from logica_negocio.api.routes_training import router as training_router

logger = logging.getLogger(__name__)

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Lifespan handler para inicio y cierre de la aplicación."""
    logger.info("🚀 DEMAND-24 API iniciando — Fase 4")
    logger.info("Documentación disponible en: http://localhost:8000/docs")
    yield
    logger.info("🛑 DEMAND-24 API cerrando")


app = FastAPI(
    title="DEMAND-24 API",
    description=(
        "Sistema Inteligente de Predicción de Demanda — MiniMarket La 24 S.A.S.\n\n"
        "**Endpoints disponibles:**\n"
        "- `/api/v1/health` — Estado del sistema\n"
        "- `/api/v1/skus` — Gestión de SKUs\n"
        "- `/api/v1/predictions` — Consulta de predicciones\n"
        "- `/api/v1/training` — Entrenamiento del modelo\n"
        "- `/api/v1/alerts` — Gestión de alertas de stock\n"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────
# Permite peticiones desde el frontend React (Fase 5)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────
app.include_router(health_router, prefix=API_PREFIX)
app.include_router(skus_router, prefix=API_PREFIX)
app.include_router(predictions_router, prefix=API_PREFIX)
app.include_router(training_router, prefix=API_PREFIX)
app.include_router(alerts_router, prefix=API_PREFIX)
