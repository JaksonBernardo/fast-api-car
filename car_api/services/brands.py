from typing import Union, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Brand
from car_api.schemas.brands import BrandSchema, BrandPublicSchema, BrandListPublicSchema, BrandUpdateSchema
from car_api.repositories.brands import BrandRepository

class BrandService:

    @staticmethod
    async def create_brand(db: AsyncSession, brand: Brand) -> BrandPublicSchema:

        brand_exists = await BrandRepository.verify_if_exists_brand_name(db, brand.name)

        if brand_exists:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Brand já existe"
            )
        
        new_brand = Brand(
            name = brand.name,
            description = brand.description,
            is_active = brand.is_active
        )
        
        new_brand = await BrandRepository.save(db, new_brand)

        return new_brand
    
    @staticmethod
    async def delete_brand(db: AsyncSession, brand_id: int) -> None:

        brand_exists = await BrandRepository.verify_if_exists_brand_id(db, brand_id)

        if not brand_exists:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Essa brand não existe"
            )
        
        cars_by_brand_id = await BrandRepository.verify_if_exists_car_by_brand_id(db, brand_id)

        if cars_by_brand_id:

            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Essa brand tem carros associados, não pode ser deletada"
            )
        
        await BrandRepository.delete_by_id(db, brand_id)

    @staticmethod
    async def get_brand_by_id(db: AsyncSession, brand_id: int) -> BrandPublicSchema:

        brand_exists = await BrandRepository.verify_if_exists_brand_id(db, brand_id)

        if not brand_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Essa brand não existe"
            )
        
        brand = await BrandRepository.get_brand_by_id(db, brand_id)

        return brand

    @staticmethod
    async def get_brands(db: AsyncSession, offset: int, limit: int, search: Union[str, None], is_active: bool) -> BrandListPublicSchema:

        if search:

            search = f"%{search}%"

        brands = await BrandRepository.get_brands(db, offset, limit, search, is_active)

        return brands

    @staticmethod
    async def update_brand(db: AsyncSession, brand_data: Dict, brand_id: int) -> BrandPublicSchema:

        brand_exists = await BrandRepository.verify_if_exists_brand_id(db, brand_id)

        if not brand_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Essa brand não existe"
            )
        

        brand = await BrandRepository.get_brand_by_id(db, brand_id)

        if "name" in brand_data and brand_data["name"] != brand.name:

            brand_name_exists = await BrandRepository.verify_if_exists_brand_name(db, brand_data["name"])

            if brand_name_exists:

                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail = "Nome da marca já existente"
                )
            
        for field, value in brand_data.items():

            setattr(brand, field, value)

        nwe_branch = await BrandRepository.update_brand(db, brand)

        return nwe_branch