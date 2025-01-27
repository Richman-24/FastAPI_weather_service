from fastapi import APIRouter, HTTPException, status
import httpx

from app.cities.repository import CityRepo
from app.weather.repository import WeatherRepo


router = APIRouter(
    prefix="/weather",
    tags=[
        "Погода",
    ],
)


@router.get("/current/", summary="Получить текущую погоду по координатам")
async def get_current_weather(latitude: float, longitude: float) -> dict:
    async with httpx.AsyncClient() as client:
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "surface_pressure", "wind_speed_10m"],
        }

        response = await client.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})

            return {
                "current_weather": {
                    "temperature": current.get(
                        "temperature_2m",
                        None,
                    ),
                    "windspeed": current.get(
                        "wind_speed_10m",
                        None,
                    ),
                    "pressure": current.get(
                        "surface_pressure",
                        None,
                    ),
                }
            }
        else:
            raise HTTPException(
                status_code=response.status_code, detail="Ошибка запроса к АПИ"
            )


@router.get("/", summary="Получить погоду по городу и времени")
async def get_wheather_in_city(
    city_name: str, time: int, params: str
) -> dict:
    # Получаем город. Проверяем, что он существует.
    city = await CityRepo.get_city_by_name(city_name.lower())
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Для этого города прогноз не отслеживается",
        )

    # Получаем погоду для этого города по времени.
    weather = await WeatherRepo.get_weather_by_city_and_time(
        city_id=city.id, time=time, params=params
    )
    return weather
