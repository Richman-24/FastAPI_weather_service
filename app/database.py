from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


db_url = "sqlite+aiosqlite:///weather.db"
engine = create_async_engine(db_url)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    abstract=True


class User(Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    
    cities = relationship('CityUser', back_populates='user')


class City(Model):
    __tablename__ = 'cities'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    
    users = relationship('CityUser', back_populates='city')
    weather = relationship("Weather", back_populates="city")


class CityUser(Model):
    __tablename__ = 'city_user'

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), primary_key=True)

    user = relationship('User', back_populates='cities')
    city = relationship('City', back_populates='users')


class Weather(Model):
    __tablename__ = 'weather'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[str] = mapped_column()
    temperature: Mapped[float] = mapped_column()
    pressure: Mapped[float] = mapped_column()
    humidity: Mapped[float] = mapped_column()
    windspeed: Mapped[float] = mapped_column()
    
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city = relationship("City", back_populates="weather")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
