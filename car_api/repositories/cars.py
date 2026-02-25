from typing import Optional, Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete, or_
from sqlalchemy.orm import selectinload

from car_api.models import Car, FuelType, TransmissionType
from car_api.schemas.cars import (
    CarSchema,
    CarUpdateSchema,
    CarPublicSchema,
    CarListPublicSchema
)

class CarRepository:

    @staticmethod
    async def save(db: AsyncSession, new_car: Car) -> Car:

        db.add(new_car)
        await db.commit()
        await db.refresh(new_car)

        return new_car
    
    @staticmethod
    async def get_cars(
        db: AsyncSession, 
        offset: int, 
        limit: int, 
        search: Union[str, None], 
        brand_id: Union[int, None], 
        owner_id: Union[int, None],
        fuel_type: Union[FuelType, None],
        transmission: Union[TransmissionType, None]
    ) -> List[CarPublicSchema]:

        query = select(Car).options(selectinload(Car.brand), selectinload(Car.owner))

        if search:

            query = query.where(
                or_(
                    Car.model.ilike(search),
                    Car.plate.ilike(search)
                )
            )

        if brand_id:

            query = query.where(
                Car.brand_id == brand_id
            )

        if owner_id:

            query = query.where(
                Car.owner_id == owner_id
            )

        if fuel_type:

            query = query.where(
                Car.fuel_type == fuel_type
            )

        if transmission:

            query = query.where(
                Car.transmission == transmission
            )

        query = query.offset(offset).limit(limit)

        cars = await db.execute(query)

        return cars.scalars().all()

    @staticmethod
    async def verify_if_plate_exists(db: AsyncSession, plate: str) -> bool:

        plate_exists = await db.scalar(
            select(exists().where(Car.plate == plate))
        )

        return plate_exists

    @staticmethod
    async def verify_if_exists_by_id(db: AsyncSession, car_id: int) -> bool:

        car_exists = await db.scalar(
            select(exists().where(Car.id == car_id))
        )

        return car_exists
    
    @staticmethod
    async def delete_car(db: AsyncSession, car_id: int) -> None:

        await db.execute(
            delete(Car).where(Car.id == car_id)
        )

        await db.commit()

    @staticmethod
    async def get_car_by_id(db: AsyncSession, car_id: int) -> Car:

        car = await db.scalar(
            select(Car).where(Car.id == car_id)
        )

        return car

    @staticmethod
    async def update_car(db: AsyncSession, car: Car) -> Car:

        await db.commit()
        await db.refresh(car)

        car = await db.scalar(
            select(Car)
            .options(selectinload(Car.brand), selectinload(Car.owner))
            .where(Car.id == car.id)
        )

        return car

