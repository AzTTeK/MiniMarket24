"""
DEMAND-24 — Repository: SkuRepository

Maneja todas las operaciones CRUD sobre la tabla 'sku'.
Sigue el Repository Pattern: aisla la lógica de datos de la lógica de negocio.
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logica_negocio.database.models.sku import Sku
from logica_negocio.database.schemas.sku import SkuCreate, SkuRead, SkuUpdate

logger = logging.getLogger(__name__)


class SkuRepository:
    """
    Repository para operaciones CRUD sobre SKUs.

    Recibe una sesión de SQLAlchemy por inyección de dependencias.
    Nunca crea su propia sesión — la recibe del caller.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, sku_data: SkuCreate) -> SkuRead:
        """
        Crea un nuevo SKU en la BD.

        Args:
            sku_data: DTO con sku_code y description.

        Returns:
            SkuRead con el SKU creado (incluye id y timestamps).

        Raises:
            ValueError: Si el sku_code ya existe (violación UNIQUE).
        """
        logger.info("Creando SKU: sku_code=%s", sku_data.sku_code)

        db_sku = Sku(**sku_data.model_dump())

        try:
            self.db.add(db_sku)
            self.db.commit()
            self.db.refresh(db_sku)
        except IntegrityError:
            self.db.rollback()
            logger.error("SKU duplicado: sku_code=%s", sku_data.sku_code)
            raise ValueError(f"SKU con código '{sku_data.sku_code}' ya existe")

        logger.info("SKU creado: id=%d, sku_code=%s", db_sku.id, db_sku.sku_code)
        return SkuRead.model_validate(db_sku)

    def get_by_id(self, sku_id: int) -> Optional[SkuRead]:
        """Obtener un SKU por su ID."""
        db_sku = self.db.query(Sku).filter(Sku.id == sku_id).first()
        if db_sku is None:
            return None
        return SkuRead.model_validate(db_sku)

    def get_by_code(self, sku_code: str) -> Optional[SkuRead]:
        """Obtener un SKU por su código único."""
        db_sku = self.db.query(Sku).filter(Sku.sku_code == sku_code).first()
        if db_sku is None:
            return None
        return SkuRead.model_validate(db_sku)

    def get_all(self) -> List[SkuRead]:
        """Obtener todos los SKUs."""
        results = self.db.query(Sku).order_by(Sku.sku_code).all()
        return [SkuRead.model_validate(r) for r in results]

    def update(self, sku_id: int, sku_data: SkuUpdate) -> Optional[SkuRead]:
        """
        Actualizar un SKU existente.

        Solo actualiza los campos no-None del SkuUpdate.

        Returns:
            SkuRead actualizado o None si no existe.

        Raises:
            ValueError: Si el nuevo sku_code ya existe (violación UNIQUE).
        """
        db_sku = self.db.query(Sku).filter(Sku.id == sku_id).first()
        if db_sku is None:
            return None

        update_data = sku_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            if value is not None:
                setattr(db_sku, field_name, value)

        try:
            self.db.commit()
            self.db.refresh(db_sku)
        except IntegrityError:
            self.db.rollback()
            logger.error("Error de integridad al actualizar SKU id=%d", sku_id)
            raise ValueError(f"SKU código duplicado en actualización")

        return SkuRead.model_validate(db_sku)

    def delete(self, sku_id: int) -> bool:
        """
        Eliminar un SKU por su ID.

        Returns:
            True si se eliminó, False si no existía.
        """
        db_sku = self.db.query(Sku).filter(Sku.id == sku_id).first()
        if db_sku is None:
            return False

        self.db.delete(db_sku)
        self.db.commit()
        logger.info("SKU eliminado: id=%d", sku_id)
        return True
