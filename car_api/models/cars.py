from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_api.models import Base

# ESSA LINHA AQUI EVITA ERRO DE IMPORTAÇÃO CIRCULAR
if TYPE_CHECKING:
    from car_api.models import User


class FuelType(str, Enum):
    GASOLINE = "gasoline"
    ETHANOL = "ethanol"
    FLEX = "flex"
    DIESEL = "diesel"
    ELETRIC = "electric"
    HYBRID = "hybrid"


class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi_automatic"
    CVT = "cvt"


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        Text, default=None, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cars: Mapped[List["Car"]] = relationship("Car", back_populates="brand")


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    factory_year: Mapped[int] = mapped_column(Integer, default=None, nullable=True)
    model_year: Mapped[int] = mapped_column(Integer, default=None, nullable=True)
    color: Mapped[str] = mapped_column(String(100), default=None, nullable=True)
    plate: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    fuel_type: Mapped[FuelType] = mapped_column(String(20))
    transmission: Mapped[TransmissionType] = mapped_column(String(20))
    price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        Text, default=None, nullable=True
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id"),
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), server_default=func.now()
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="cars",
    )

    owner: Mapped["User"] = relationship("User", back_populates="cars")
