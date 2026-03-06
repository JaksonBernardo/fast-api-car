from typing import Dict, Union

from fastapi import HTTPException, status

from car_api.models import Brand
from car_api.repositories.brands import BrandRepository
from car_api.schemas.brands import (
    BrandListPublicSchema,
    BrandPublicSchema,
    BrandSchema,
)


class BrandService:
    def __init__(self, brand_repository: BrandRepository):
        self.brand_repository = brand_repository

    async def create_brand(self, brand: BrandSchema) -> BrandPublicSchema:
        brand_exists = await self.brand_repository.verify_if_exists_brand_name(
            brand.name
        )

        if brand_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Brand já existe"
            )

        new_brand = Brand(
            name=brand.name, description=brand.description, is_active=brand.is_active
        )

        new_brand = await self.brand_repository.save(new_brand)

        return new_brand

    async def delete_brand(self, brand_id: int) -> None:
        brand_exists = await self.brand_repository.verify_if_exists_brand_id(brand_id)

        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Essa brand não existe"
            )

        cars_by_brand_id = (
            await self.brand_repository.verify_if_exists_car_by_brand_id(brand_id)
        )

        if cars_by_brand_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Essa brand tem carros associados, não pode ser deletada",
            )

        await self.brand_repository.delete_by_id(brand_id)

    async def get_brand_by_id(self, brand_id: int) -> BrandPublicSchema:
        brand_exists = await self.brand_repository.verify_if_exists_brand_id(brand_id)

        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Essa brand não existe"
            )

        brand = await self.brand_repository.get_brand_by_id(brand_id)

        return brand

    async def get_brands(
        self,
        offset: int,
        limit: int,
        search: Union[str, None],
        is_active: bool,
    ) -> BrandListPublicSchema:
        if search:
            search = f"%{search}%"

        brands = await self.brand_repository.get_brands(
            offset, limit, search, is_active
        )

        return brands

    async def update_brand(self, brand_data: Dict, brand_id: int) -> BrandPublicSchema:
        brand_exists = await self.brand_repository.verify_if_exists_brand_id(brand_id)

        if not brand_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Essa brand não existe"
            )

        brand = await self.brand_repository.get_brand_by_id(brand_id)

        if "name" in brand_data and brand_data["name"] != brand.name:
            brand_name_exists = await self.brand_repository.verify_if_exists_brand_name(
                brand_data["name"]
            )

            if brand_name_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Nome da marca já existente",
                )

        for field, value in brand_data.items():
            setattr(brand, field, value)

        new_brand = await self.brand_repository.update_brand(brand)

        return new_brand
