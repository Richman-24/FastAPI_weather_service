from typing import Optional
from sqlalchemy import select
from app.database import User, new_session
from app.users.schemas import SUserUsername


class UserRepo:
    @classmethod
    async def add_one(cls, data: SUserUsername) -> User:
        async with new_session() as session:
        
            user = User(**data.model_dump())
            user.username = user.username.lower()
            
            session.add(user)
            await session.flush()
            await session.commit()
            return user

    @classmethod
    async def get_user(cls, user_id: int) -> User:
        async with new_session() as session:
            query = select(User).where(User.id == user_id)
            instance = await session.execute(query)
            result = instance.scalars().first()
            return result
 
    @classmethod
    async def get_user_by_username(cls, username: str) -> Optional[User]:
        async with new_session() as session:
            query = select(User).where(User.username == username.lower())
            instance = await session.execute(query)
            return instance.scalars().first()