"""
DEMAND-24 — Conexión a Base de Datos

Factory de SQLAlchemy Engine y SessionLocal.
Dependency `get_db` para inyección en endpoints FastAPI.

Cumple con:
- Regla VIII: DATABASE_URL desde .env via settings
- Decisión #18: Sesión inyectada desde capa superior
"""

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from logica_negocio.config.settings import settings

logger = logging.getLogger(__name__)


def _build_engine():
    """Construye el engine de SQLAlchemy según DATABASE_URL."""
    database_url = settings.DATABASE_URL

    if not database_url:
        logger.error("DATABASE_URL no configurada en .env")
        raise EnvironmentError(
            "DATABASE_URL no está definida. Revisa tu archivo .env"
        )

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(
        database_url,
        echo=settings.APP_DEBUG,
        connect_args=connect_args,
    )

    logger.info("Engine de BD creado: %s", database_url.split("@")[-1] if "@" in database_url else "local")
    return engine


def build_session_factory(engine=None):
    """
    Construye un sessionmaker vinculado al engine.

    Args:
        engine: Engine de SQLAlchemy (default: crea uno nuevo).

    Returns:
        sessionmaker configurado.
    """
    if engine is None:
        engine = _build_engine()

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency de FastAPI para inyección de sesión.

    Yields:
        Session: Sesión de SQLAlchemy lista para usar.

    Notes:
        - Cada request obtiene su propia sesión.
        - La sesión se cierra automáticamente al terminar.
    """
    session_factory = build_session_factory()
    db = session_factory()

    try:
        yield db
    finally:
        db.close()
