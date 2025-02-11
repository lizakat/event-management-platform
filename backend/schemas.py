from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    role_id: int = None
    avatar: str = None
    birthdate: str = None
    location: dict = None
    phone: str = None