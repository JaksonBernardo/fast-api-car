from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete, or_

from car_api.models import Brand
from car_api.schemas.brands import (
    BrandSchema,
    BrandUpdateSchema,
    BrandPublicSchema,
    BrandListPublicSchema
)

class BrandRepository:

    @staticmethod
    async def save(db: AsyncSession, new_brand: BrandSchema) -> BrandPublicSchema:

        db.add(new_brand)
        
        await db.commit()
        await db.refresh(new_brand)

        return new_brand
    
    @staticmethod
    async def verify_if_exists_brand_name(db: AsyncSession, brand_name: str) -> bool:

        brand = await db.scalar(
            select(exists().where(Brand.name == brand_name))
        )

        return brand

