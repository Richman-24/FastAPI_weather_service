from pydantic import BaseModel


class SCityCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
