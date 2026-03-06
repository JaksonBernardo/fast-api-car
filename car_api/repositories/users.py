from typing import Union

from sqlalchemy import delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import User
from car_api.schemas.users import (
    UserListPublicSchema,
    UserPublicSchema,
    UserSchema,
)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, new_user: User) -> UserPublicSchema:
        self.db.add(new_user)

        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_user_by_id(self, user_id: int) -> UserPublicSchema:
        user = await self.db.scalar(select(User).where(User.id == user_id))

        return user

    async def get_users(
        self, offset: int, limit: int, search: Union[str, None]
    ) -> UserListPublicSchema:
        query = select(User)

        if search:
            query = query.where(
                or_(User.username.ilike(search), User.email.ilike(search))
            )

        query = query.offset(offset).limit(limit)

        users = await self.db.execute(query)

        return users.scalars().all()

    async def delete_by_id(self, user_id: int) -> None:
        await self.db.execute(delete(User).where(User.id == user_id))

        await self.db.commit()

    async def verify_if_exists_username(self, username: str) -> bool:
        user = await self.db.scalar(select(exists().where(User.username == username)))

        return user

    async def verify_if_exists_email(self, email: str) -> bool:
        user = await self.db.scalar(select(exists().where(User.email == email)))

        return user

    async def verify_if_exists_id(self, user_id: int) -> bool:
        user = await self.db.scalar(select(exists().where(User.id == user_id)))

        return user

    async def update_user(self, user: UserPublicSchema) -> UserPublicSchema:
        await self.db.commit()
        await self.db.refresh(user)

        return user
