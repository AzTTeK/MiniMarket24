"""
DEMAND-24 — Tests: Pydantic Schemas

Verifica validaciones, parsing from_attributes, y edge cases de los DTOs.
"""

from datetime import date, datetime, timezone

import pytest

from logica_negocio.database.schemas.evaluation_fold import EvaluationFoldCreate
from logica_negocio.database.schemas.model_version import ModelVersionCreate, ModelVersionRead
from logica_negocio.database.schemas.prediction import PredictionCreate
from logica_negocio.database.schemas.sku import SkuCreate, SkuRead


class TestSkuSchemas:
    """Tests para schemas de Sku."""

    def test_sku_create_valid(self):
        """SkuCreate válido con campos requeridos."""
        sku = SkuCreate(sku_code="GROCERY I", description="Abarrotes")
        assert sku.sku_code == "GROCERY I"

    def test_sku_create_minimal(self):
        """SkuCreate con solo el campo requerido."""
        sku = SkuCreate(sku_code="DAIRY")
        assert sku.description is None

    def test_sku_read_from_attributes(self):
        """SkuRead debe funcionar con from_attributes (ORM → DTO)."""

        class FakeOrm:
            id = 1
            sku_code = "MEATS"
            description = "Carnes"
            created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
            updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        sku = SkuRead.model_validate(FakeOrm())
        assert sku.id == 1
        assert sku.sku_code == "MEATS"


class TestPredictionSchemas:
    """Tests para schemas de Prediction."""

    def test_prediction_create_valid(self):
        """PredictionCreate válido con todos los campos."""
        pred = PredictionCreate(
            sku_id=1,
            week_start=date(2026, 1, 5),
            predicted_demand=100.0,
            confidence_level=0.90,
            lower_bound=95.0,
            upper_bound=105.0,
            mape=5.0,
        )
        assert pred.predicted_demand == 100.0

    def test_prediction_create_negative_demand_raises(self):
        """predicted_demand negativa debe ser rechazada."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PredictionCreate(
                sku_id=1,
                week_start=date(2026, 1, 5),
                predicted_demand=-10.0,
            )

    def test_prediction_create_confidence_out_of_range_raises(self):
        """confidence_level > 1.0 debe ser rechazada."""
        with pytest.raises(Exception):
            PredictionCreate(
                sku_id=1,
                week_start=date(2026, 1, 5),
                predicted_demand=100.0,
                confidence_level=1.5,
            )


class TestEvaluationFoldSchemas:
    """Tests para schemas de EvaluationFold."""

    def test_evaluation_fold_create_valid(self):
        """EvaluationFoldCreate con métricas válidas."""
        fold = EvaluationFoldCreate(
            fold_number=1,
            mape=12.5,
            mae=45.0,
            bias=-2.3,
        )
        assert fold.fold_number == 1
        assert fold.bias == -2.3

    def test_fold_number_must_be_positive(self):
        """fold_number < 1 debe ser rechazado."""
        with pytest.raises(Exception):
            EvaluationFoldCreate(fold_number=0, mape=10.0)


class TestModelVersionSchemas:
    """Tests para schemas de ModelVersion."""

    def test_model_version_create_valid(self):
        """ModelVersionCreate con todos los campos."""
        mv = ModelVersionCreate(
            version="v1.0.0",
            random_seed=42,
            n_splits=5,
            xgboost_params={"max_depth": 6},
            acceptance_criteria_met=True,
        )
        assert mv.version == "v1.0.0"
        assert mv.xgboost_params["max_depth"] == 6

    def test_model_version_read_from_attributes(self):
        """ModelVersionRead con from_attributes."""

        class FakeOrm:
            id = 1
            version = "v1.0.0"
            training_date = datetime(2026, 4, 1, tzinfo=timezone.utc)
            random_seed = 42
            n_splits = 5
            xgboost_params = {"max_depth": 6}
            acceptance_criteria_met = True
            created_at = datetime(2026, 4, 1, tzinfo=timezone.utc)

        mv = ModelVersionRead.model_validate(FakeOrm())
        assert mv.version == "v1.0.0"
        assert mv.acceptance_criteria_met is True
