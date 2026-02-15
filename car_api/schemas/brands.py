from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime

class BrandSchema(BaseModel):

    name: str
    description: Optional[str] = None
    is_active: bool = True

    @field_validator("name")
    def name_min_length(cls, v):

        if len(v.strip()) < 2:

            raise ValueError("Name deve ter pelo menos 2 caracteres")

        return v.strip()
    

class BrandUpdateSchema(BaseModel):

    name: Optional[str]
    description: Optional[str] = None
    is_active: Optional[bool] = True

    @field_validator("name")
    def name_min_length(cls, v):

        if len(v.strip()) < 2:

            raise ValueError("Name deve ter pelo menos 2 caracteres")

        return v.strip()


class BrandPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BrandListPublicSchema(BaseModel):

    brands: List[BrandPublicSchema]
    offset: int
    limit: int
