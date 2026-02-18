from typing import Optional, List,  Literal
from decimal import Decimal
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime

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
    model_config = ConfigDict(from_attributes = True)

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

