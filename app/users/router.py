from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.users.repository import UserRepo
from app.users.schemas import SUserUsername


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, summary="Регистрация пользователя"
)
async def create_user(data: Annotated[SUserUsername, Depends()]) -> dict:
    existing_user = await UserRepo.get_user_by_username(data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким юзернэймом уже существует",
        )

    user = await UserRepo.add_one(data=data)
    return {"id": user.id}


@router.get("/{user_id}", summary="Получить пользователя")
async def get_user(user_id: int) -> dict:
    user = await UserRepo.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не найден",
        )
    return {"username": user.username}
