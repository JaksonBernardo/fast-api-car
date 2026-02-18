from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.services.brands import BrandService
from car_api.core.database import get_session
from car_api.schemas.brands import (
    BrandSchema,
    BrandUpdateSchema,
    BrandPublicSchema,
    BrandListPublicSchema
)

brands_routes = APIRouter(prefix="/api/brands", tags=["Brands"])

@brands_routes.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = BrandPublicSchema,
    summary = "Criando uma nova brand"
)
async def create_brand(
    brand: BrandSchema,
    db: AsyncSession = Depends(get_session)
) -> BrandPublicSchema:
    
    new_brand = await BrandService.create_brand(
        db,
        brand
    )

    return new_brand

@brands_routes.delete(
    path = "{brand_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Deletando uma branch"
)
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    
    await BrandService.delete_brand(db, brand_id)

