"""
DEMAND-24 — API Router: SKUs

Endpoints para consulta y creación de SKUs.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import ErrorResponse
from logica_negocio.core.database import get_db
from logica_negocio.core.services import DemandService
from logica_negocio.database.schemas.sku import SkuCreate, SkuRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skus", tags=["SKUs"])


@router.get(
    "",
    response_model=List[SkuRead],
    summary="Listar todos los SKUs",
    description="Obtiene todos los SKUs registrados en el sistema.",
)
def list_skus(db: Session = Depends(get_db)) -> List[SkuRead]:
    """Lista todos los SKUs registrados, ordenados por código."""
    service = DemandService(db)
    return service.get_all_skus()


@router.get(
    "/{sku_id}",
    response_model=SkuRead,
    summary="Obtener un SKU",
    description="Obtiene los detalles de un SKU por su ID.",
    responses={404: {"model": ErrorResponse}},
)
def get_sku(sku_id: int, db: Session = Depends(get_db)) -> SkuRead:
    """Obtiene un SKU específico por su ID."""
    service = DemandService(db)
    sku = service.get_sku_by_id(sku_id)

    if sku is None:
        raise HTTPException(
            status_code=404,
            detail=f"SKU con id={sku_id} no encontrado",
        )

    return sku


@router.post(
    "",
    response_model=SkuRead,
    status_code=201,
    summary="Crear un SKU",
    description="Registra un nuevo SKU en el sistema.",
    responses={409: {"model": ErrorResponse}},
)
def create_sku(sku_data: SkuCreate, db: Session = Depends(get_db)) -> SkuRead:
    """Crea un nuevo SKU con código único."""
    service = DemandService(db)

    try:
        created = service.create_sku(sku_data)
    except ValueError as err:
        raise HTTPException(status_code=409, detail=str(err))

    logger.info("SKU creado via API: %s", sku_data.sku_code)
    return created
