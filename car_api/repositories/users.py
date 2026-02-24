from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete, or_

from car_api.models import User
from car_api.schemas.users import (
    UserPublicSchema,
    UserListPublicSchema,
    UserSchema
)

class UserRepository:

    @staticmethod
    async def save(db: AsyncSession, new_user: UserSchema) -> UserPublicSchema:

        db.add(new_user)

        await db.commit()
        await db.refresh(new_user)

        return new_user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserPublicSchema:

        user = await db.scalar(
            select(User).where(User.id == user_id)
        )

        return user

    @staticmethod
    async def get_users(db: AsyncSession, offset: int, limit: int, search: Union[str, None]) -> UserListPublicSchema:

        query = select(User)

        if search:

            query = query.where(
                or_(
                    User.username.ilike(search),
                    User.email.ilike(search)
                )
            )

        query = query.offset(offset).limit(limit)

        users = await db.execute(query)

        return users.scalars().all()

    @staticmethod
    async def delete_by_id(db: AsyncSession, user_id: int) -> None:

        await db.execute(
            delete(User).where(User.id == user_id)
        )

        await db.commit()
    
    @staticmethod
    async def verify_if_exists_username(db: AsyncSession, username: str) -> bool:

        user = await db.scalar(
            select(exists().where(User.username == username))
        )

        return user
    
    @staticmethod
    async def verify_if_exists_email(db: AsyncSession, email: str) -> bool:

        user = await db.scalar(
            select(exists().where(User.email == email))
        )

        return user
    
    @staticmethod
    async def verify_if_exists_id(db: AsyncSession, user_id: int) -> bool:

        user = await db.scalar(
            select(exists().where(User.id == user_id))
        )

        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user: UserPublicSchema) -> UserPublicSchema:

        await db.commit()
        await db.refresh(user)

        return user

