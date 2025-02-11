from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    google_id: str
    role_id: int = None
    avatar: str = None
    birthdate: datetime = None
    location: dict = None
    phone: str = None