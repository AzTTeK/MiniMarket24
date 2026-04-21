"""
DEMAND-24 — Repository: ModelVersionRepository

Maneja operaciones CRUD sobre la tabla 'model_version'.
Permite registrar y consultar versiones de modelos entrenados.
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logica_negocio.database.models.model_version import ModelVersion
from logica_negocio.database.schemas.model_version import (
    ModelVersionCreate,
    ModelVersionRead,
    ModelVersionUpdate,
)

logger = logging.getLogger(__name__)


class ModelVersionRepository:
    """
    Repository para operaciones CRUD sobre versiones de modelos.

    Métodos de negocio adicionales:
    - get_by_version: busca por version string (UNIQUE)
    - get_latest: obtiene la versión más reciente
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, version_data: ModelVersionCreate) -> ModelVersionRead:
        """
        Registra una nueva versión de modelo.

        Raises:
            ValueError: Si la versión ya existe (violación UNIQUE).
        """
        logger.info("Registrando modelo: version=%s", version_data.version)

        db_version = ModelVersion(**version_data.model_dump())

        try:
            self.db.add(db_version)
            self.db.commit()
            self.db.refresh(db_version)
        except IntegrityError:
            self.db.rollback()
            logger.error("Versión duplicada: %s", version_data.version)
            raise ValueError(f"Versión '{version_data.version}' ya existe")

        logger.info("Modelo registrado: id=%d, version=%s", db_version.id, db_version.version)
        return ModelVersionRead.model_validate(db_version)

    def get_by_id(self, version_id: int) -> Optional[ModelVersionRead]:
        """Obtener una versión de modelo por su ID."""
        result = self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if result is None:
            return None
        return ModelVersionRead.model_validate(result)

    def get_by_version(self, version: str) -> Optional[ModelVersionRead]:
        """Obtener una versión de modelo por su string de versión."""
        result = self.db.query(ModelVersion).filter(ModelVersion.version == version).first()
        if result is None:
            return None
        return ModelVersionRead.model_validate(result)

    def get_latest(self) -> Optional[ModelVersionRead]:
        """Obtener la versión de modelo más reciente (por training_date)."""
        result = (
            self.db.query(ModelVersion)
            .order_by(ModelVersion.training_date.desc())
            .first()
        )
        if result is None:
            return None
        return ModelVersionRead.model_validate(result)

    def get_all(self) -> List[ModelVersionRead]:
        """Obtener todas las versiones de modelo, más recientes primero."""
        results = (
            self.db.query(ModelVersion)
            .order_by(ModelVersion.training_date.desc())
            .all()
        )
        return [ModelVersionRead.model_validate(r) for r in results]

    def update(self, version_id: int, version_data: ModelVersionUpdate) -> Optional[ModelVersionRead]:
        """Actualizar metadata de una versión de modelo."""
        db_version = self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if db_version is None:
            return None

        update_data = version_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            if value is not None:
                setattr(db_version, field_name, value)

        try:
            self.db.commit()
            self.db.refresh(db_version)
        except IntegrityError:
            self.db.rollback()
            logger.error("Error de integridad al actualizar versión id=%d", version_id)
            raise ValueError("Error de integridad al actualizar versión")

        return ModelVersionRead.model_validate(db_version)

    def delete(self, version_id: int) -> bool:
        """Eliminar una versión de modelo por su ID."""
        db_version = self.db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if db_version is None:
            return False

        self.db.delete(db_version)
        self.db.commit()
        logger.info("Versión eliminada: id=%d", version_id)
        return True
