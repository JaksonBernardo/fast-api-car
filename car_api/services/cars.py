from typing import Union, List, Dict, Callable
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Car, FuelType, TransmissionType, User
from car_api.repositories.cars import CarRepository
from car_api.repositories.brands import BrandRepository
from car_api.repositories.users import UserRepository
from car_api.schemas.cars import (
    CarSchema,
    CarUpdateSchema,
    CarPublicSchema,
    CarListPublicSchema
)

class CarServices:

    @staticmethod
    async def create_car(db: AsyncSession, car_data: CarSchema) -> CarPublicSchema:

        brand_exists = await BrandRepository.verify_if_exists_brand_id(db, car_data.brand_id)

        if not brand_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Marca de carro não encontrada"
            )
        
        owner_exists = await UserRepository.verify_if_exists_id(db, car_data.owner_id)

        if not owner_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Proprietário não encontrado"
            )

        plate_exists = await CarRepository.verify_if_plate_exists(db, car_data.plate)

        if plate_exists:

            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Esta placa já está inserida no sistema"
            )

        new_car = Car(
            model = car_data.model,
            factory_year = car_data.factory_year, 
            model_year = car_data.model_year, 
            color = car_data.color, 
            plate = car_data.plate, 
            fuel_type = car_data.fuel_type, 
            transmission = car_data.transmission,
            price = car_data.price, 
            description = car_data.description, 
            is_available = car_data.is_available,
            brand_id = car_data.brand_id,
            owner_id = car_data.owner_id,
        )

        new_car = await CarRepository.save(db, new_car)

        brand_infos = await BrandRepository.get_brand_by_id(db, car_data.brand_id)

        owner_infos = await UserRepository.get_user_by_id(db, car_data.owner_id)

        new_car.brand = brand_infos
        new_car.owner = owner_infos

        return new_car

    @staticmethod
    async def delete_car(db: AsyncSession, car_id: int, current_user: User, verify_car_ownership: Callable) -> None:

        car = await CarRepository.get_car_by_id(db, car_id)

        if not car:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Carro não encontrado"
            )
        
        verify_car_ownership(current_user, car.owner_id)

        await CarRepository.delete_car(db, car_id)

    @staticmethod
    async def get_car_by_id(db: AsyncSession, car_id: int,  current_user: User, verify_car_ownership: Callable) -> CarPublicSchema:

        car_exists = await CarRepository.verify_if_exists_by_id(db, car_id)

        if not car_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Carro não encontrado"
            )
        
        car = await CarRepository.get_car_by_id(db, car_id)

        brand_infos = await BrandRepository.get_brand_by_id(db, car.brand_id)

        owner_infos = await UserRepository.get_user_by_id(db, car.owner_id)

        car.brand = brand_infos
        car.owner = owner_infos

        verify_car_ownership(current_user, car.owner_id)

        return car

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

        if search:

            search = f"%{search}%"

        cars = await CarRepository.get_cars(db, offset, limit, search, brand_id, owner_id, fuel_type, transmission)

        return cars
    
    @staticmethod
    async def update_car(db: AsyncSession, car_data: Dict, car_id: int, current_user: User, verify_car_ownership: Callable) -> CarPublicSchema:

        car_exists = await CarRepository.verify_if_exists_by_id(db, car_id)

        if not car_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Carro não encontrado"
            )
        
        car = await CarRepository.get_car_by_id(db, car_id)

        verify_car_ownership(current_user, car.owner_id)

        if "plate" in car_data and car_data["plate"] != car.plate:

            plate_exists = await CarRepository.verify_if_plate_exists(db, car_data["plate"])

            if plate_exists:

                raise HTTPException(
                    status_code = status.HTTP_409_CONFLICT,
                    detail = "Placa do veículo já existente"
                )
            
        if "price" in car_data and car_data["price"] <= 0:

            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Preço do veículo tem que ser maior que zero"
            )
        
        if "model" in car_data and not car_data["model"]:

            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Modelo do veículo inválido"
            )
        
        if "brand_id" in car_data:

            brand_exists = await BrandRepository.verify_if_exists_brand_id(db, car_data["brand_id"])

            if not brand_exists:

                raise HTTPException(
                    status_code = status.HTTP_409_CONFLICT,
                    detail = "Marca/Brand não encontrada"
                )
            
        if "owner_id" in car_data:
        
            owner_exists = await UserRepository.verify_if_exists_id(db, car_data["owner_id"])

            if not owner_exists:

                raise HTTPException(
                    status_code = status.HTTP_409_CONFLICT,
                    detail = "Proprietário do veículo não encontrado"
                )

        for field, value in car_data.items():

            setattr(car, field, value)

        new_car = await CarRepository.update_car(db, car)

        return new_car




