from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.services.cars import CarServices
from car_api.core.database import get_session
from car_api.schemas.cars import (
    CarSchema,
    CarUpdateSchema,
    CarPublicSchema,
    CarListPublicSchema
)


car_routes = APIRouter(prefix="/api/cars", tags=["Cars"])


@car_routes.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = CarPublicSchema,
    summary = "Criando um registro de carro"
)
async def create_cars(
    car_data: CarSchema,
    db: AsyncSession = Depends(get_session)
) -> CarPublicSchema:
    
    new_car = await CarServices.create_car(db, car_data)

    return new_car


@car_routes.get(
    path = "/",
    status_code = status.HTTP_200_OK,
    response_model = CarListPublicSchema,
    summary = "Listando carros"
)
async def get_cars(
    offset: int = Query(0, ge = 0, description = "Número de registros a serem pulados"),
    limit: int = Query(100, ge = 1, le = 100, description = "Limite de registros a serem listados"),
    search: Optional[str] = Query(None, description = "Buscar por nome ou placa"),
    db: AsyncSession = Depends(get_session)
) -> CarListPublicSchema:
    
    cars = await CarServices.get_cars(
        db,
        offset,
        limit,
        search
    )

    return {
        "cars": cars,
        "offset": offset,
        "limit": limit
    }


@car_routes.get(
    path = "/{car_id}",
    status_code = status.HTTP_200_OK,
    response_model = CarPublicSchema,
    summary = "Selecionando um carro específico"
)
async def get_car_by_id(
    car_id: int,
    db: AsyncSession = Depends(get_session)
) -> CarPublicSchema:
    
    car = await CarServices.get_car_by_id(db, car_id)

    return car


@car_routes.delete(
    path = "/{car_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Deletando um carro"
)
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_session)
) -> None:
    
    await CarServices.delete_car(db, car_id)


