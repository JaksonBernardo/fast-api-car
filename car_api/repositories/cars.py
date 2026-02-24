from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete, or_
from sqlalchemy.orm import selectinload

from car_api.models import Car
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



