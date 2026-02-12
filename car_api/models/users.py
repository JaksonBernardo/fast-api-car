from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from car_api.models import Base

# ESSA LINHA AQUI EVITA ERRO DE IMPORTAÇÃO CIRCULAR
if TYPE_CHECKING:
    
    from car_api.models import Car

class User(Base):

    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255), nullable = False)
    email: Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default = func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        onupdate = func.now(), 
        server_default = func.now()
    )
    
    cars: Mapped[List['Car']] = relationship(
        'Car',
        back_populates = "owner"
    )
