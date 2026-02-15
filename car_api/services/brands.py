from typing import Union, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Brand
from car_api.schemas.brands import BrandSchema, BrandPublicSchema
from car_api.repositories.brands import BrandRepository

class BrandService:

    @staticmethod
    async def create_brand(db: AsyncSession, brand: Brand) -> BrandPublicSchema:

        brand_exists = await BrandRepository.verify_if_exists_brand_name(db, brand.name)

        if brand_exists:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Brand já existe"
            )
        
        new_brand = Brand(
            name = brand.name,
            description = brand.description,
            is_active = brand.is_active
        )
        
        new_brand = await BrandRepository.save(db, new_brand)

        return new_brand