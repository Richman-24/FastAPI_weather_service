from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables
from app.users.router import router as user_router
from app.cities.router import router as cities_router
from app.weather.router import router as weather_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("Database ready to work")

    yield

app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
app.include_router(cities_router)
app.include_router(weather_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
