"""
DEMAND-24 — Tests para MLConfig Utils
Verificación de cargadores de env para subir coverage.
"""

import os
import pytest
from modulo_analitico.config.ml_config import (
    _get_ml_env_int,
    _get_ml_env_float,
    _get_ml_env_bool,
    MLConfig
)

def test_ml_env_getters():
    """Prueba las funciones auxiliares de carga de entorno."""
    os.environ["TEST_INT"] = "100"
    assert _get_ml_env_int("TEST_INT", 50) == 100
    assert _get_ml_env_int("NON_EXISTENT", 50) == 50
    assert _get_ml_env_int("TEST_INT", "invalid") == 100 # Should use raw if possible
    
    os.environ["TEST_FLOAT"] = "0.75"
    assert _get_ml_env_float("TEST_FLOAT", 0.5) == 0.75
    assert _get_ml_env_float("NON_EXISTENT", 0.5) == 0.5
    
    os.environ["TEST_BOOL"] = "true"
    assert _get_ml_env_bool("TEST_BOOL", False) is True
    os.environ["TEST_BOOL"] = "0"
    assert _get_ml_env_bool("TEST_BOOL", True) is False

def test_ml_config_validation():
    """Prueba las validaciones de MLConfig."""
    from dataclasses import replace
    config = MLConfig()
    
    # Caso válido
    config.validate()
    
    # Casos inválidos
    with pytest.raises(ValueError, match="CONFIDENCE_LEVEL"):
        replace(config, CONFIDENCE_LEVEL=1.5).validate()
        
    with pytest.raises(ValueError, match="MIN_WEEKS_HISTORY"):
        replace(config, MIN_WEEKS_HISTORY=0).validate()
