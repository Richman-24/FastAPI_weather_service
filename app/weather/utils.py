from datetime import datetime
from typing import List

from fastapi import HTTPException, status
import httpx
from sqlalchemy import delete

from app.cities.repository import CityRepo
from app.database import City, Weather, new_session


async def update_forecast(city_name=None):
    """Обновляет прогноз погоды для ВСЕХ ГОРОДОВ ИЗ БАЗЫ / КОНКРЕТНОГО ГОРОДА."""
    async with new_session() as session:
        async with session.begin():
            try:
                async with httpx.AsyncClient() as client:
                    if city_name is None:
                        # Получаем СПИСОК ОБЪЕКТОВ всех городов из базы.
                        cities = await CityRepo.get_all_cities()
                        
                        if cities is None or len(cities) == 0:
                            return
                    else:
                        # Получаем один объект города и сохраняем его в списке.
                        city_obj = await CityRepo.get_city_by_name(city_name)
                        cities = [city_obj,]

                    # Запрашиваем прогноз у АПИ.
                    forecast_data = await fetch_forecast(client, cities)

                    # Подготавливаем данные для записи в базу данных.
                    prepared_forecast_data = await prepare_weather_data(cities, forecast_data)

                    # Удаляем существующий прогноз из базы.
                    await delete_old_forecast(session, cities)

                    # Записываем новый прогноз в базу данных.
                    session.add_all(prepared_forecast_data)
                    print("## Обновление прогноза проведено")
                    await session.commit()
                    
            except Exception as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка при обновлении прогноза: {e}",
                )

async def fetch_forecast(client: httpx.AsyncClient, cities: List[City]):
    """Получает от Open-meteo API прогноз погоды для СПИСКА ГОРОДОВ cities."""

    url = "https://api.open-meteo.com/v1/forecast"
    latitudes = [city.latitude for city in cities]
    longitudes = [city.longitude for city in cities]
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
        ],
        "timezone": "auto",
        "forecast_days": 1,
    }

    response = await client.get(url, params=params)
    response.raise_for_status()

    return response.json()

async def prepare_weather_data(cities, forecast_data):
    """Подготавливает записи о погоде для сохранения в базе данных."""

    weather_entries = []

    if isinstance(forecast_data, dict):
        forecast_data = [forecast_data]

    for city, hourly_data in zip(cities, forecast_data):
        if "hourly" in hourly_data:
            for time, temp, pressure, humidity, windspeed in zip(
                hourly_data["hourly"]["time"],
                hourly_data["hourly"]["temperature_2m"],
                hourly_data["hourly"]["surface_pressure"],
                hourly_data["hourly"]["relative_humidity_2m"],
                hourly_data["hourly"]["wind_speed_10m"],
            ):
                weather_entry = Weather(
                    city_id=city.id,
                    timestamp=time,
                    temperature=temp,
                    pressure=pressure,
                    humidity=humidity,
                    windspeed=windspeed,
                )
                weather_entries.append(weather_entry)
    return weather_entries

async def delete_old_forecast(session, cities: int):
    """Удаляет существующий прогноз для городов cities."""

    city_ids = [city.id for city in cities]
    query = delete(Weather).where(Weather.city_id.in_(city_ids))
    await session.execute(query)

async def format_data(hour: int):
    """Приводит время введённое пользователем к формату iso8601."""
    today = datetime.now()
    combined_datetime = today.replace(hour=hour, minute=0, second=0, microsecond=0)
    formatted_date = combined_datetime.strftime("%Y-%m-%dT%H:%M")

    return formatted_date