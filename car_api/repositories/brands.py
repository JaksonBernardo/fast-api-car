from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete, or_

from car_api.models import Brand, Car
from car_api.schemas.brands import (
    BrandSchema,
    BrandUpdateSchema,
    BrandPublicSchema,
    BrandListPublicSchema
)

class BrandRepository:

    @staticmethod
    async def save(db: AsyncSession, new_brand: Brand) -> BrandPublicSchema:

        db.add(new_brand)
        
        await db.commit()
        await db.refresh(new_brand)

        return new_brand
    
    @staticmethod
    async def verify_if_exists_car_by_brand_id(db: AsyncSession, brand_id: int) -> bool:

        cars = await db.scalars(
            select(Car).where(Car.brand_id == brand_id)
        )

        return len(cars.all()) > 0

    @staticmethod
    async def verify_if_exists_brand_name(db: AsyncSession, brand_name: str) -> bool:

        brand = await db.scalar(
            select(exists().where(Brand.name == brand_name))
        )

        return brand
    
    @staticmethod
    async def verify_if_exists_brand_id(db: AsyncSession, brand_id: int) -> bool:

        brand = await db.scalar(
            select(exists().where(Brand.id == brand_id))
        )

        return brand
    
    @staticmethod
    async def delete_by_id(db: AsyncSession, brand_id: int) -> None:

        await db.execute(
            delete(Brand).where(Brand.id == brand_id)
        )

        await db.commit()

