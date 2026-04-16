"""
DEMAND-24 — Módulo Analítico, Configuración

Configuración centralizada de hiperparámetros y constantes del ML Engine.
Todos los valores se cargan desde .env vía settings.py de logica_negocio.
"""

from .ml_config import MLConfig, ml_config

__all__ = ["MLConfig", "ml_config"]
