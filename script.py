from contextlib import asynccontextmanager

from app.weather.utils import update_forecast
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI


from app.database import create_tables
from app.users.router import router as user_router
from app.cities.router import router as cities_router
from app.weather.router import router as weather_router


scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("2. База данных готова к работе")
    
    await update_forecast()
    print("1. Обновление прогноза выполнено")

    scheduler.start()
    scheduler.add_job(update_forecast, 'interval', minutes=15)
    print("0. Автобновление прогноза запущено")

    yield

    scheduler.shutdown()
    print("-1. Автобновление прогноза остановлено")

app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
app.include_router(cities_router)
app.include_router(weather_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
