from fastapi import HTTPException, status
from sqlalchemy import select

from app.database import Weather, new_session
from app.weather.utils import format_data


class WeatherRepo:
    @classmethod
    async def get_weather_by_city_and_time(
        cls, city_id: int, time: str, params: str
    ) -> dict:
        async with new_session() as session:
            # Получаем погоду для города из базы данных
            query = select(Weather).where(Weather.city_id == city_id)
            weather_data = await session.execute(query)
            weather_instance = weather_data.scalars().all()

            # Фильтруем погоду по времени 
            _time = await format_data(time) # Приводим время к формату iso8601
            weather_at_time = [
                weather for weather in weather_instance if weather.timestamp == _time
            ]

            if not weather_at_time:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Погода на указанное время не найдена",
                )

            # Формируем ответ в зависимости от запрашиваемых параметров
            response = {}
            
            _params = params.split(', ') # Приводит параметры к формату списка
            
            if _params == []:
                _params = ["temperature", "presure", "windspeed", "humidity"]    
            
            for param in _params:
                if param == "temperature":
                    response["temperature"] = weather_at_time[0].temperature
                elif param == "humidity":
                    response["humidity"] = weather_at_time[0].humidity
                elif param == "windspeed":
                    response["windspeed"] = weather_at_time[0].windspeed
                elif param == "presure":
                    response["presure"] = weather_at_time[0].pressure

            return response
