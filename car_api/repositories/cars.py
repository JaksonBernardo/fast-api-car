from typing import List, Union

from sqlalchemy import delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from car_api.models import Car, FuelType, TransmissionType
from car_api.schemas.cars import CarPublicSchema


class CarRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, new_car: Car) -> Car:
        self.db.add(new_car)
        await self.db.commit()
        await self.db.refresh(new_car)

        return new_car

    async def get_cars(
        self,
        offset: int,
        limit: int,
        search: Union[str, None],
        brand_id: Union[int, None],
        owner_id: Union[int, None],
        fuel_type: Union[FuelType, None],
        transmission: Union[TransmissionType, None],
    ) -> List[CarPublicSchema]:
        query = select(Car).options(
            selectinload(Car.brand), selectinload(Car.owner)
        )

        if search:
            query = query.where(
                or_(Car.model.ilike(search), Car.plate.ilike(search))
            )

        if brand_id:
            query = query.where(Car.brand_id == brand_id)

        if owner_id:
            query = query.where(Car.owner_id == owner_id)

        if fuel_type:
            query = query.where(Car.fuel_type == fuel_type)

        if transmission:
            query = query.where(Car.transmission == transmission)

        query = query.offset(offset).limit(limit)

        cars = await self.db.execute(query)

        return cars.scalars().all()

    async def verify_if_plate_exists(self, plate: str) -> bool:
        plate_exists = await self.db.scalar(
            select(exists().where(Car.plate == plate))
        )

        return plate_exists

    async def verify_if_exists_by_id(self, car_id: int) -> bool:
        car_exists = await self.db.scalar(select(exists().where(Car.id == car_id)))

        return car_exists

    async def delete_car(self, car_id: int) -> None:
        await self.db.execute(delete(Car).where(Car.id == car_id))

        await self.db.commit()

    async def get_car_by_id(self, car_id: int) -> Car:
        car = await self.db.scalar(select(Car).where(Car.id == car_id))

        return car

    async def update_car(self, car: Car) -> Car:
        await self.db.commit()
        await self.db.refresh(car)

        car = await self.db.scalar(
            select(Car)
            .options(selectinload(Car.brand), selectinload(Car.owner))
            .where(Car.id == car.id)
        )

        return car
