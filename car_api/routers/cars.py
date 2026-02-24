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


