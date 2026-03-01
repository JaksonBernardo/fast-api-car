from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_session
from car_api.core.security import get_current_user, verify_car_ownership
from car_api.models import FuelType, TransmissionType, User
from car_api.schemas.cars import (
    CarListPublicSchema,
    CarPublicSchema,
    CarSchema,
    CarUpdateSchema,
)
from car_api.services.cars import CarServices

car_routers = APIRouter(prefix="/api/cars", tags=["Cars"])


@car_routers.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=CarPublicSchema,
    summary="Criando um registro de carro",
)
async def create_cars(
    car_data: CarSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CarPublicSchema:

    new_car = await CarServices.create_car(db, car_data)

    return new_car


@car_routers.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=CarListPublicSchema,
    summary="Listando carros",
)
async def get_cars(
    offset: int = Query(0, ge=0, description="Número de registros a serem pulados"),
    limit: int = Query(
        100, ge=1, le=100, description="Limite de registros a serem listados"
    ),
    search: Optional[str] = Query(None, description="Buscar por nome ou placa"),
    brand_id: Optional[int] = Query(
        None, description="Buscar por uma marca específica"
    ),
    owner_id: Optional[int] = Query(
        None, description="Buscar por um proprietário específico"
    ),
    fuel_type: Optional[FuelType] = Query(
        None, description="Buscar por um tipo de combustível"
    ),
    transmission: Optional[TransmissionType] = Query(
        None, description="Buscar por um tipo de transmissão"
    ),
    db: AsyncSession = Depends(get_session),
) -> CarListPublicSchema:

    cars = await CarServices.get_cars(
        db, offset, limit, search, brand_id, owner_id, fuel_type, transmission
    )

    return {"cars": cars, "offset": offset, "limit": limit}


@car_routers.get(
    path="/{car_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary="Selecionando um carro específico",
)
async def get_car_by_id(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CarPublicSchema:

    car = await CarServices.get_car_by_id(
        db, car_id, current_user, verify_car_ownership
    )

    return car


@car_routers.delete(
    path="/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletando um carro",
)
async def delete_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> None:

    await CarServices.delete_car(db, car_id)


@car_routers.put(
    path="{car_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarPublicSchema,
    summary="Atualizando um registro de carro",
)
async def update_car(
    car_id: int,
    car_data: CarUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> CarPublicSchema:

    car_data = car_data.model_dump(exclude_unset=True)

    car = await CarServices.update_car(
        db, car_data, car_id, current_user, verify_car_ownership
    )

    return car
