from pydantic import BaseModel


class SUserUsername(BaseModel):
    username: str


class SUserId(BaseModel):
    id: int