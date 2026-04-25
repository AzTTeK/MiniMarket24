"""
DEMAND-24 — Tests: Integración DemandPredictor + Persistencia

Verifica que save_predictions_to_db y save_training_results_to_db
funcionan correctamente con BD en memoria.
"""

from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logica_negocio.database.models import Base
from logica_negocio.database.models.sku import Sku
from logica_negocio.database.repositories.prediction_repository import PredictionRepository
from logica_negocio.database.repositories.model_version_repository import ModelVersionRepository
from modulo_analitico.predictor import DemandPredictor


@pytest.fixture
def integration_db():
    """BD en memoria con un SKU de prueba pre-creado."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # Crear SKU de prueba
    sku = Sku(sku_code="GROCERY I", description="Test")
    session.add(sku)
    session.commit()
    session.refresh(sku)

    yield session, sku.id

    session.close()
    engine.dispose()


class TestPredictorSavePredictions:
    """Tests para DemandPredictor.save_predictions_to_db()."""

    def test_save_predictions_to_db_success(self, integration_db):
        """save_predictions_to_db debe guardar predicciones correctamente."""
        session, sku_id = integration_db
        predictor = DemandPredictor()

        predictions_df = pd.DataFrame([
            {
                "sku_id": sku_id,
                "week_start": date(2026, 1, 5),
                "predicted_demand": 100.0,
                "confidence_level": 0.90,
                "lower_bound": 95.0,
                "upper_bound": 105.0,
                "mape": 5.0,
            },
            {
                "sku_id": sku_id,
                "week_start": date(2026, 1, 12),
                "predicted_demand": 120.0,
                "confidence_level": 0.90,
                "lower_bound": 110.0,
                "upper_bound": 130.0,
                "mape": 7.0,
            },
        ])

        count = predictor.save_predictions_to_db(predictions_df, session)
        assert count == 2

        # Verificar que se guardaron en BD
        repo = PredictionRepository(session)
        all_preds = repo.get_all_by_sku(sku_id)
        assert len(all_preds) == 2

    def test_save_predictions_missing_columns_raises(self, integration_db):
        """DataFrame sin columnas requeridas deve lanzar ValueError."""
        session, _ = integration_db
        predictor = DemandPredictor()

        incomplete_df = pd.DataFrame([{"sku_id": 1, "week_start": date(2026, 1, 5)}])

        with pytest.raises(ValueError, match="Columnas faltantes"):
            predictor.save_predictions_to_db(incomplete_df, session)


class TestPredictorSaveTrainingResults:
    """Tests para DemandPredictor.save_training_results_to_db()."""

    def test_save_training_results_no_metrics_raises(self, integration_db):
        """Sin métricas disponibles debe lanzar RuntimeError."""
        session, _ = integration_db
        predictor = DemandPredictor()

        with pytest.raises(RuntimeError, match="No hay métricas"):
            predictor.save_training_results_to_db("v1.0.0", session)

    def test_save_training_results_success(self, integration_db):
        """Con métricas simuladas, debe guardar versión del modelo."""
        session, _ = integration_db
        predictor = DemandPredictor()

        # Simular que train() ya corrió poniendo métricas directamente
        predictor._metrics = {
            "mape_mean": 15.0,
            "mape_std": 3.0,
            "acceptance_criteria_met": True,
        }

        predictor.save_training_results_to_db("v1.0.0", session)

        # Verificar que se guardó la versión
        model_repo = ModelVersionRepository(session)
        version = model_repo.get_by_version("v1.0.0")
        assert version is not None
        assert version.version == "v1.0.0"
        assert version.random_seed == 42  # Default de MLConfig
