from typing import List
from sqlalchemy import select
from app.database import City, CityUser, new_session
from app.cities.schemas import SCityCreate


class CityRepo:
    @classmethod
    async def add_one(cls, user_id: int, data: SCityCreate) -> City:
       async with new_session() as session:
            new_city = City(**data.model_dump())
            new_city.name = new_city.name.lower()
            
            session.add(new_city)
            await session.flush()

    @classmethod
    async def get_cities_by_user(cls, user_id: int) -> List[str | None]:
        async with new_session() as session:
            query = select(City).join(CityUser).where(CityUser.user_id == user_id)
            instance = await session.execute(query)
            result = instance.scalars().all()

            return [city.name for city in result]
    
    @classmethod
    async def get_city_by_name(cls, name: str) -> City | None:
        async with new_session() as session:
            query = select(City).where(City.name == name)
            instance = await session.execute(query)
            return instance.scalar_one_or_none()

    
    @classmethod
    async def get_all_cities(cls) -> List[str | None]:
        async with new_session() as session:
            query = select(City)
            instance = await session.execute(query)
            result = instance.scalars().all()
            
            return [city.name for city in result]


class CityUserRepo:
    @classmethod
    async def create_relation(cls, user_id: int, city_id: int):
        async with new_session() as session:
                user_relation = CityUser(user_id=user_id, city_id=city_id)
                session.add(user_relation)
                await session.commit()


    @classmethod
    async def get_relation(cls, user_id: int, city_id: int) -> CityUser | None:
        async with new_session() as session:
            query = select(CityUser).where(
                CityUser.user_id == user_id,
                CityUser.city_id == city_id
            )
            instance = await session.execute(query)
            return instance.scalar_one_or_none()