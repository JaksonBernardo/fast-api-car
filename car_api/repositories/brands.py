from typing import Union

from sqlalchemy import delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Brand, Car
from car_api.schemas.brands import BrandListPublicSchema, BrandPublicSchema


class BrandRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, new_brand: Brand) -> BrandPublicSchema:
        self.db.add(new_brand)

        await self.db.commit()
        await self.db.refresh(new_brand)

        return new_brand

    async def get_brands(
        self,
        offset: int,
        limit: int,
        search: Union[str, None],
        is_active: bool,
    ) -> BrandListPublicSchema:
        query = select(Brand)

        if search:
            query = query.where(
                or_(Brand.name.ilike(search), Brand.description.ilike(search))
            )

        if is_active is not None:
            query = query.where(Brand.is_active == is_active)

        query = query.offset(offset).limit(limit)

        brands = await self.db.execute(query)

        return brands.scalars().all()

    async def verify_if_exists_car_by_brand_id(self, brand_id: int) -> bool:
        cars = await self.db.scalars(select(Car).where(Car.brand_id == brand_id))

        return len(cars.all()) > 0

    async def verify_if_exists_brand_name(self, brand_name: str) -> bool:
        brand = await self.db.scalar(select(exists().where(Brand.name == brand_name)))

        return brand

    async def verify_if_exists_brand_id(self, brand_id: int) -> bool:
        brand = await self.db.scalar(select(exists().where(Brand.id == brand_id)))

        return brand

    async def delete_by_id(self, brand_id: int) -> None:
        await self.db.execute(delete(Brand).where(Brand.id == brand_id))

        await self.db.commit()

    async def get_brand_by_id(self, brand_id: int) -> BrandPublicSchema:
        brand = await self.db.scalar(select(Brand).where(Brand.id == brand_id))

        return brand

    async def update_brand(self, brand: BrandPublicSchema) -> BrandPublicSchema:
        await self.db.commit()
        await self.db.refresh(brand)

        return brand
