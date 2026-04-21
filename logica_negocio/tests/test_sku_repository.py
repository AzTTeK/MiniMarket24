"""
DEMAND-24 — Tests: SkuRepository

Tests CRUD completos + manejo de duplicados y edge cases.
"""

import pytest

from logica_negocio.database.repositories.sku_repository import SkuRepository
from logica_negocio.database.schemas.sku import SkuCreate, SkuUpdate


class TestSkuRepository:
    """Tests para SkuRepository CRUD."""

    def test_create_sku_success(self, test_db):
        """Crear un SKU deve retornar un SkuRead con ID asignado."""
        repo = SkuRepository(test_db)
        sku = repo.create(SkuCreate(sku_code="GROCERY I", description="Abarrotes"))

        assert sku.id is not None
        assert sku.sku_code == "GROCERY I"
        assert sku.description == "Abarrotes"

    def test_create_sku_duplicate_raises(self, test_db):
        """Crear SKU con código duplicado debe lanzar ValueError."""
        repo = SkuRepository(test_db)
        repo.create(SkuCreate(sku_code="BEVERAGES"))
        with pytest.raises(ValueError, match="ya existe"):
            repo.create(SkuCreate(sku_code="BEVERAGES"))

    def test_get_by_id_existing(self, test_db):
        """Obtener SKU por ID existente deve retornar el SKU."""
        repo = SkuRepository(test_db)
        created = repo.create(SkuCreate(sku_code="DAIRY"))
        found = repo.get_by_id(created.id)

        assert found is not None
        assert found.sku_code == "DAIRY"

    def test_get_by_id_nonexistent(self, test_db):
        """Obtener SKU por ID inexistente deve retornar None."""
        repo = SkuRepository(test_db)
        assert repo.get_by_id(999) is None

    def test_get_by_code_existing(self, test_db):
        """Obtener SKU por código existente deve retornar el SKU."""
        repo = SkuRepository(test_db)
        repo.create(SkuCreate(sku_code="MEATS"))
        found = repo.get_by_code("MEATS")

        assert found is not None
        assert found.sku_code == "MEATS"

    def test_get_by_code_nonexistent(self, test_db):
        """Obtener SKU por código inexistente deve retornar None."""
        repo = SkuRepository(test_db)
        assert repo.get_by_code("NONEXISTENT") is None

    def test_get_all_empty(self, test_db):
        """get_all en BD vacía deve retornar lista vacía."""
        repo = SkuRepository(test_db)
        assert repo.get_all() == []

    def test_get_all_multiple(self, test_db):
        """get_all deve retornar todos los SKUs ordenados por código."""
        repo = SkuRepository(test_db)
        repo.create(SkuCreate(sku_code="BEVERAGES"))
        repo.create(SkuCreate(sku_code="AUTOMOTIVE"))

        all_skus = repo.get_all()

        assert len(all_skus) == 2
        assert all_skus[0].sku_code == "AUTOMOTIVE"  # Ordenado alfabéticamente
        assert all_skus[1].sku_code == "BEVERAGES"

    def test_update_existing(self, test_db):
        """Actualizar un SKU existente deve reflejar los cambios."""
        repo = SkuRepository(test_db)
        created = repo.create(SkuCreate(sku_code="OLD_CODE"))
        updated = repo.update(created.id, SkuUpdate(description="Nueva descripción"))

        assert updated is not None
        assert updated.description == "Nueva descripción"

    def test_update_nonexistent(self, test_db):
        """Actualizar un SKU inexistente deve retornar None."""
        repo = SkuRepository(test_db)
        assert repo.update(999, SkuUpdate(description="nope")) is None

    def test_delete_existing(self, test_db):
        """Eliminar un SKU existente deve retornar True y eliminarlo."""
        repo = SkuRepository(test_db)
        created = repo.create(SkuCreate(sku_code="TO_DELETE"))

        assert repo.delete(created.id) is True
        assert repo.get_by_id(created.id) is None

    def test_delete_nonexistent(self, test_db):
        """Eliminar un SKU inexistente deve retornar False."""
        repo = SkuRepository(test_db)
        assert repo.delete(999) is False
