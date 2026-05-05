"""
DEMAND-24 — Capa de Servicios (Service Layer)

Orquestador entre los endpoints REST y los módulos internos.
Toda lógica de negocio pasa por aquí — los endpoints son "tontos".

Cumple con:
- Regla I: SoC — API no toca ML directo
- Decisión #12: Backend accede ML solo vía DemandPredictor
- Decisión #18: Sesión BD inyectada desde capa superior
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from logica_negocio.database.repositories import (
    AlertRepository,
    ModelVersionRepository,
    PredictionRepository,
    SkuRepository,
)
from logica_negocio.database.schemas import (
    AlertRead,
    ModelVersionRead,
    PredictionRead,
    SkuCreate,
    SkuRead,
)

logger = logging.getLogger(__name__)


class DemandService:
    """
    Capa de servicios que orquesta las operaciones del sistema DEMAND-24.

    Responsabilidades:
    - Consultar SKUs, predicciones, modelos vía repositories
    - Disparar entrenamiento vía DemandPredictor (lazy import)
    - Gestionar alertas vía AlertEngine
    - NUNCA accede a ML internals directamente

    Usage:
        service = DemandService(db_session)
        skus = service.get_all_skus()
    """

    def __init__(self, db: Session):
        self._db = db
        self._sku_repo = SkuRepository(db)
        self._prediction_repo = PredictionRepository(db)
        self._model_version_repo = ModelVersionRepository(db)
        self._alert_repo = AlertRepository(db)

    # ── SKU Operations ──────────────────────────────────────────

    def get_all_skus(self) -> List[SkuRead]:
        """Lista todos los SKUs registrados."""
        return self._sku_repo.get_all()

    def get_sku_by_id(self, sku_id: int) -> Optional[SkuRead]:
        """Obtiene un SKU por su ID."""
        return self._sku_repo.get_by_id(sku_id)

    def create_sku(self, sku_data: SkuCreate) -> SkuRead:
        """Crea un nuevo SKU."""
        return self._sku_repo.create(sku_data)

    # ── Prediction Operations ───────────────────────────────────

    def get_predictions_by_sku(self, sku_id: int) -> List[PredictionRead]:
        """Obtiene todas las predicciones de un SKU."""
        return self._prediction_repo.get_all_by_sku(sku_id)

    def get_all_predictions(self) -> List[PredictionRead]:
        """Obtiene todas las predicciones del sistema."""
        return self._prediction_repo.get_all()

    # ── Model Operations ────────────────────────────────────────

    def get_latest_model(self) -> Optional[ModelVersionRead]:
        """Obtiene la versión más reciente del modelo."""
        return self._model_version_repo.get_latest()

    def get_all_models(self) -> List[ModelVersionRead]:
        """Lista todas las versiones de modelo."""
        return self._model_version_repo.get_all()

    # ── Training Orchestration ──────────────────────────────────

    def trigger_training(self) -> Dict[str, Any]:
        """
        Dispara el pipeline completo de entrenamiento del modelo.

        Flujo (Decisión Arquitectónica #9):
            load_data → prepare_data → train → save_training_results_to_db

        Returns:
            Diccionario con resultados del entrenamiento incluyendo métricas.

        Raises:
            RuntimeError: Si el pipeline falla en cualquier etapa.
        """
        logger.info("Iniciando pipeline de entrenamiento vía DemandService")

        # Lazy import para evitar acoplamiento circular (Decisión #12)
        from modulo_analitico.predictor import DemandPredictor

        predictor = DemandPredictor()

        try:
            logger.info("Etapa 1/4: Cargando datos...")
            predictor.load_data()

            logger.info("Etapa 2/4: Preparando datos (agregación + features)...")
            predictor.prepare_data()

            logger.info("Etapa 3/4: Entrenando modelo...")
            training_results = predictor.train()

            logger.info("Etapa 4/4: Persistiendo resultados en BD...")
            predictor.save_training_results_to_db(self._db)

        except FileNotFoundError as err:
            logger.error("Dataset no encontrado: %s", err)
            raise RuntimeError(
                "No se encontró el dataset de entrenamiento. "
                "Verifica que los archivos CSV estén en data/raw/"
            ) from err
        except Exception as err:
            logger.error("Error en pipeline de entrenamiento: %s", err)
            raise RuntimeError(
                f"Error durante el entrenamiento: {str(err)}"
            ) from err

        logger.info("Pipeline de entrenamiento completado exitosamente")
        return training_results

    # ── Alert Operations ────────────────────────────────────────

    def get_active_alerts(self) -> List[AlertRead]:
        """Obtiene alertas activas (no atendidas)."""
        return self._alert_repo.get_active()

    def get_all_alerts(self) -> List[AlertRead]:
        """Obtiene todas las alertas."""
        return self._alert_repo.get_all()

    def get_alerts_by_sku(self, sku_id: int) -> List[AlertRead]:
        """Obtiene alertas de un SKU específico."""
        return self._alert_repo.get_by_sku(sku_id)

    def acknowledge_alert(self, alert_id: int) -> Optional[AlertRead]:
        """Marca una alerta como atendida."""
        return self._alert_repo.acknowledge(alert_id)

    def check_stock_alerts(self, stock_levels: Dict[int, int]) -> List[AlertRead]:
        """
        Ejecuta el motor de alertas para detectar quiebres de stock.

        Args:
            stock_levels: {sku_id: stock_actual}
        """
        from logica_negocio.core.alert_engine import AlertEngine

        engine = AlertEngine(self._db)
        return engine.check_stock_alerts(stock_levels)
