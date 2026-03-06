from typing import Callable, Dict, List, Union

from fastapi import HTTPException, status

from car_api.models import Car, FuelType, TransmissionType, User
from car_api.repositories.brands import BrandRepository
from car_api.repositories.cars import CarRepository
from car_api.repositories.users import UserRepository
from car_api.schemas.cars import CarPublicSchema, CarSchema


class CarServices:
    def __init__(
        self,
        car_repository: CarRepository,
        brand_repository: BrandRepository,
        user_repository: UserRepository,
    ):
        self.car_repository = car_repository
        self.brand_repository = brand_repository
        self.user_repository = user_repository

    async def create_car(self, car_data: CarSchema) -> CarPublicSchema:
        brand_exists = await self.brand_repository.verify_if_exists_brand_id(
            car_data.brand_id
        )

        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Marca de carro não encontrada",
            )

        owner_exists = await self.user_repository.verify_if_exists_id(
            car_data.owner_id
        )

        if not owner_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proprietário não encontrado",
            )

        plate_exists = await self.car_repository.verify_if_plate_exists(car_data.plate)

        if plate_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta placa já está inserida no sistema",
            )

        new_car = Car(
            model=car_data.model,
            factory_year=car_data.factory_year,
            model_year=car_data.model_year,
            color=car_data.color,
            plate=car_data.plate,
            fuel_type=car_data.fuel_type,
            transmission=car_data.transmission,
            price=car_data.price,
            description=car_data.description,
            is_available=car_data.is_available,
            brand_id=car_data.brand_id,
            owner_id=car_data.owner_id,
        )

        new_car = await self.car_repository.save(new_car)

        brand_infos = await self.brand_repository.get_brand_by_id(car_data.brand_id)

        owner_infos = await self.user_repository.get_user_by_id(car_data.owner_id)

        new_car.brand = brand_infos
        new_car.owner = owner_infos

        return new_car

    async def delete_car(
        self,
        car_id: int,
        current_user: User,
        verify_car_ownership: Callable,
    ) -> None:
        car = await self.car_repository.get_car_by_id(car_id)

        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado"
            )

        verify_car_ownership(current_user, car.owner_id)

        await self.car_repository.delete_car(car_id)

    async def get_car_by_id(
        self,
        car_id: int,
        current_user: User,
        verify_car_ownership: Callable,
    ) -> CarPublicSchema:
        car_exists = await self.car_repository.verify_if_exists_by_id(car_id)

        if not car_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado"
            )

        car = await self.car_repository.get_car_by_id(car_id)

        brand_infos = await self.brand_repository.get_brand_by_id(car.brand_id)

        owner_infos = await self.user_repository.get_user_by_id(car.owner_id)

        car.brand = brand_infos
        car.owner = owner_infos

        verify_car_ownership(current_user, car.owner_id)

        return car

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
        if search:
            search = f"%{search}%"

        cars = await self.car_repository.get_cars(
            offset, limit, search, brand_id, owner_id, fuel_type, transmission
        )

        return cars

    async def update_car(
        self,
        car_data: Dict,
        car_id: int,
        current_user: User,
        verify_car_ownership: Callable,
    ) -> CarPublicSchema:
        car_exists = await self.car_repository.verify_if_exists_by_id(car_id)

        if not car_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado"
            )

        car = await self.car_repository.get_car_by_id(car_id)

        verify_car_ownership(current_user, car.owner_id)

        if "plate" in car_data and car_data["plate"] != car.plate:
            plate_exists = await self.car_repository.verify_if_plate_exists(
                car_data["plate"]
            )

            if plate_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Placa do veículo já existente",
                )

        if "price" in car_data and car_data["price"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Preço do veículo tem que ser maior que zero",
            )

        if "model" in car_data and not car_data["model"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Modelo do veículo inválido",
            )

        if "brand_id" in car_data:
            brand_exists = await self.brand_repository.verify_if_exists_brand_id(
                car_data["brand_id"]
            )

            if not brand_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Marca/Brand não encontrada",
                )

        if "owner_id" in car_data:
            owner_exists = await self.user_repository.verify_if_exists_id(
                car_data["owner_id"]
            )

            if not owner_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Proprietário do veículo não encontrado",
                )

        for field, value in car_data.items():
            setattr(car, field, value)

        new_car = await self.car_repository.update_car(car)

        return new_car
