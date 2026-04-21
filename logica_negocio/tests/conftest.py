"""
DEMAND-24 — Conftest para tests de Fase 3

Fixture compartido: base de datos SQLite en memoria para tests aislados.
Cada test obtiene una sesión limpia con las tablas creadas fresh.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logica_negocio.database.models import Base


@pytest.fixture
def test_db():
    """
    Crea una BD SQLite en memoria con todas las tablas del schema.

    Yields:
        Session: Sesión de SQLAlchemy lista para usar.

    Notes:
        - Cada test obtiene tablas vacías (aislamiento total).
        - SQLite en memoria es rápido y no requiere instalar nada.
        - Compatible con los ORM models (JSON cae a TEXT en SQLite).
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    yield session

    session.close()
    engine.dispose()
