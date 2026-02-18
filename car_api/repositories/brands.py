from typing import List, Union
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
    async def get_brands(db: AsyncSession, offset: int, limit: int, search: Union[str, None], is_active: bool) -> BrandListPublicSchema:

        query = select(Brand)

        if search:

            query = query.where(
                or_(
                    Brand.name.ilike(search),
                    Brand.description.ilike(search)
                )
            )

        if is_active is not None:

            query = query.where(Brand.is_active == is_active)

        query = query.offset(offset).limit(limit)

        brands = await db.execute(query)

        return brands.scalars().all()

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

    @staticmethod
    async def get_brand_by_id(db: AsyncSession, brand_id: int) -> BrandPublicSchema:

        brand = await db.scalar(
            select(Brand).where(Brand.id == brand_id)
        )

        return brand

    @staticmethod
    async def update_brand(db: AsyncSession, brand: BrandPublicSchema) -> BrandPublicSchema:

        await db.commit()
        await db.refresh(brand)

        return brand
