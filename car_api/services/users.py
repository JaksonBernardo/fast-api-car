from typing import Union, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.schemas.users import UserSchema
from car_api.models import User
from car_api.repositories.users import UserRepository
from car_api.core.security import get_password_hash
from car_api.schemas.users import UserPublicSchema, UserListPublicSchema

class UserService:

    @staticmethod
    async def create_user(db: AsyncSession, user: UserSchema) -> User:

        username_exists = await UserRepository.verify_if_exists_username(db, user.username)
        emails_exists = await UserRepository.verify_if_exists_email(db, user.email)

        if username_exists or emails_exists:

            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Nome ou email já está em uso"
            )
        
        hashed_password = get_password_hash(user.password)

        new_user = User(
            username = user.username,
            email = user.email,
            password = hashed_password
        )

        return await UserRepository.save(db, new_user)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:

        user_exists = await UserRepository.verify_if_exists_id(db, user_id)

        if not user_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Usuário não encontrado"
            )
        
        await UserRepository.delete_by_id(db, user_id)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserPublicSchema | None:

        user_exists = await UserRepository.verify_if_exists_id(db, user_id)

        if not user_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Usuário não encontrado"
            )
        
        return await UserRepository.get_by_id(db, user_id)
    
    @staticmethod
    async def list_users(db: AsyncSession, offset: int, limit: int, search: Union[str, None]) -> UserListPublicSchema:

        if search:

            search = f"%{search}%"

        users = await UserRepository.get_users(db, offset, limit, search)

        return users
    
    @staticmethod
    async def update_user(db: AsyncSession, user_data: Dict, user_id: int) -> UserPublicSchema:

        user_exists = await UserRepository.verify_if_exists_id(db, user_id)

        if not user_exists:

            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Usuário não encontrado"
            )
        
        user = await UserRepository.get_by_id(db, user_id)
        
        if "email" in user_data and user_data["email"] != user.email:
        
            email_exists = await UserRepository.verify_if_exists_email(db, user_data["email"])

            if email_exists:

                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail = "Email indisponível"
                )
        
        if "password" in user_data:

            user_data["password"] = get_password_hash(user_data["password"])

        for field, value in user_data.items():

            setattr(user, field, value)

        new_user = await UserRepository.update_user(db, user)

        return new_user
