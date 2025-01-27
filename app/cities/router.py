from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.cities.repository import CityRepo, CityUserRepo
from app.cities.schemas import SCityCreate
from app.users.repository import UserRepo


router = APIRouter(prefix="/cities", tags=["Города",])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Добавить город")
async def add_city(user_id: int, city_data: Annotated[SCityCreate, Depends()]):
    # Проверяем, существует ли пользователь
    check_user = await UserRepo.get_user(user_id)
    if check_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден",
        )
    
    # Проверяем, существует ли город
    existing_city = await CityRepo.get_city_by_name(city_data.name.lower())
    if existing_city:
        
        # Проверяем наличие связи с пользователем
        user_city_relation = await CityUserRepo.get_relation(user_id=user_id, city_id=existing_city.id)
        if user_city_relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Город уже добавлен в список",
            )
        else:
            # Если связи нет, создаем ее
            await CityUserRepo.create_relation(user_id=user_id, city_id=existing_city.id)
    else:
        # Если город не существует, создаем новый
        try:
            new_city = await CityRepo.add_one(user_id=user_id, data=city_data)
            await CityUserRepo.create_relation(user_id=user_id, city_id=existing_city.id)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Город уже добавлен в список",
            )
    return {"OK": f"Город {new_city.name.title()} успешно добавлен"}


@router.get("/{user_id}", summary="Получить список городов пользователя")
async def get_cities_by_user(user_id: int) -> List[str | None]:
    check_user = await UserRepo.get_user(user_id)
    if check_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден",
        )

    cities = await CityRepo.get_cities_by_user(user_id)
    
    return cities

@router.get("/", summary="Получить ВСЕ города")
async def get_all_cities() -> List[str | None]:
    cities = await CityRepo.get_all_cities()
    return cities