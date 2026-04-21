"""
DEMAND-24 — SQLAlchemy Model: Sku

Representa un producto (SKU) en el catálogo del minimarket.
Mapea directamente a la tabla 'sku' en Supabase.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from .base import Base


def _utcnow() -> datetime:
    """Genera timestamp UTC actual (evita datetime.utcnow deprecated)."""
    return datetime.now(timezone.utc)


class Sku(Base):
    """
    Modelo ORM para la tabla 'sku'.

    Campos:
        id: Identificador autoincremental (BIGSERIAL en PostgreSQL).
        sku_code: Código único del SKU (e.g., 'GROCERY I', 'BEVERAGES').
        description: Descripción textual del SKU.
        created_at: Timestamp de creación.
        updated_at: Timestamp de última actualización.
    """

    __tablename__ = "sku"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    def __repr__(self) -> str:
        return f"<Sku(id={self.id}, sku_code='{self.sku_code}')>"
