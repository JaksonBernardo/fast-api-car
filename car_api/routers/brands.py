from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import User
from car_api.services.brands import BrandService
from car_api.core.database import get_session
from car_api.core.security import (
    get_current_user,
    get_password_hash
)
from car_api.schemas.brands import (
    BrandSchema,
    BrandUpdateSchema,
    BrandPublicSchema,
    BrandListPublicSchema
)

brands_routers = APIRouter(prefix="/api/brands", tags=["Brands"])


@brands_routers.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = BrandPublicSchema,
    summary = "Criando uma nova brand"
)
async def create_brand(
    brand: BrandSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> BrandPublicSchema:
    
    new_brand = await BrandService.create_brand(
        db,
        brand
    )

    return new_brand


@brands_routers.get(
    path = "/",
    status_code = status.HTTP_200_OK,
    response_model = BrandListPublicSchema,
    summary = "Listando brands",
)
async def get_brands(
    offset: int = Query(0, ge = 0, description = "Número de registros a serem pulados"),
    limit: int = Query(10, ge = 1, le = 10, description = "Limite de registros a serem listados"),
    search: Optional[str] = Query(None, description = "Buscar por nome ou descrição"),
    is_active: Optional[bool] = Query(None, description = "Filtrar por marcas ativas"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> BrandListPublicSchema:
    
    brands = await BrandService.get_brands(db, offset, limit, search, is_active)

    return {
        "brands": brands,
        "offset": offset,
        "limit": limit
    }


@brands_routers.get(
    path = "/{brand_id}",
    status_code = status.HTTP_200_OK,
    response_model = BrandPublicSchema,
    summary = "Coletando brand por id"
)
async def get_brand_by_id(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> BrandPublicSchema:
    
    brand = await BrandService.get_brand_by_id(db, brand_id)

    return brand


@brands_routers.delete(
    path = "/{brand_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Deletando uma branch"
)
async def delete_brand(
    brand_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> None:
    
    await BrandService.delete_brand(db, brand_id)


@brands_routers.put(
    path = "/{brand_id}",
    status_code = status.HTTP_200_OK,
    response_model = BrandPublicSchema,
    summary = "Atualizando brand",
)
async def update_brand(
    brand_id: int,
    brand_data : BrandUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> BrandPublicSchema:
    
    updated_data = brand_data.model_dump(exclude_unset = True)

    new_brand = await BrandService.update_brand(db, updated_data, brand_id)

    return new_brand
