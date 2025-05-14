from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, Dict, List



class UserBase(BaseModel):
    email: str
    name: str
    surname: str
    avatar: Optional[str] = None
    birthdate: Optional[date] = None
    location: Optional[Dict] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    avatar: Optional[str] = None
    birthdate: Optional[date] = None
    location: Optional[Dict] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role_id: Optional[int] = None
    created_at: datetime


class UserLogin(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: EmailStr
    password: str


class UserStatistics(BaseModel):
    events_visited: int
    last_visit: str
    statuses: Dict[str, int]

class UserProfileData(BaseModel):
    name: str
    surname: str
    email: str
    phone: str
    location: str
    birthdate: str
    statistics: UserStatistics
    favorite_tags: List[str]


class EventBase(BaseModel):
     title: str
     description: Optional[str] = None
     location: Optional[Dict] = None
     date: date
     time: time
     max_participants: Optional[int] = None
     price: Optional[float] = None
     image: Optional[str] = None

class EventCreate(EventBase):
     organizer_id: int


#verification code

class GenerateCodeRequest(BaseModel):
    email: EmailStr

class ValidateCodeRequest(BaseModel):
    email: EmailStr
    code: str
