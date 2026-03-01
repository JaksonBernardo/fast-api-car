from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from car_api.models import FuelType, TransmissionType
from car_api.schemas.brands import BrandPublicSchema
from car_api.schemas.users import UserPublicSchema


class CarSchema(BaseModel):
    model: str
    factory_year: int
    model_year: int
    color: str
    plate: str
    fuel_type: FuelType
    transmission: TransmissionType
    price: Decimal
    description: Optional[str] = None
    is_available: bool = True
    brand_id: int
    owner_id: int

    @field_validator("model")
    def model_min_length(cls, v: str):

        if len(v.strip()) < 2:
            raise ValueError("O modelo do carro deve ter pelo menos 2 caracteres")

        return v.strip()

    @field_validator("color")
    def color_min_length(cls, v: str):

        if len(v.strip()) < 2:
            raise ValueError("A cor do carro deve ter pelo menos 2 caracteres")

        return v.strip()

    @field_validator("plate")
    def plate_max_min_length(cls, v: str):

        PLATE = v.strip().upper()

        if len(PLATE) < 7 or len(PLATE) > 10:
            raise ValueError("A placa do carro deve ter de 7 a 10 caracteres")

        return PLATE

    @field_validator("factory_year", "model_year")
    def year_validation(cls, v):

        if v < 1900 or v > 2030:
            raise ValueError("Ano deve estar entre 1900 e 2030")

        return v

    @field_validator("price")
    def price_value(cls, v):

        if v <= 0:
            raise ValueError("O valor do veículo deve ser maior que zero")

        return v


class CarUpdateSchema(BaseModel):
    model: Optional[str] = None
    factory_year: Optional[int] = None
    model_year: Optional[int] = None
    color: Optional[str] = None
    plate: Optional[str] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    is_available: Optional[bool] = True
    brand_id: Optional[int] = None
    owner_id: Optional[int] = None


class CarPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model: str
    factory_year: int
    model_year: int
    color: str
    plate: str
    fuel_type: FuelType
    transmission: TransmissionType
    price: Decimal
    description: Optional[str] = None
    is_available: bool = True
    brand_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    brand: BrandPublicSchema
    owner: UserPublicSchema


class CarListPublicSchema(BaseModel):
    cars: List[CarPublicSchema]
    offset: int
    limit: int
