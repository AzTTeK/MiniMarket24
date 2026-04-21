"""
DEMAND-24 — Base declarativa SQLAlchemy

Punto único de definición del Base para todos los ORM models.
Todos los models deben heredar de este Base.

Cumple con:
- Regla I: Separación estricta (esta capa solo conoce BD)
- Regla III: ORM + Repository Pattern
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
