from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, Dict


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int


class RegistrationStatusBase(BaseModel):
    status: str


class RegistrationStatusResponse(RegistrationStatusBase):
    id: int


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


class UserResponse(UserBase):
    id: int
    role_id: Optional[int] = None
    created_at: datetime

class UserLogin(UserBase):
    email: EmailStr
    password: str

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[Dict] = None
    date: date
    max_participants: Optional[int] = None
    price: Optional[float] = None
    image: Optional[str] = None


class EventCreate(EventBase):
    organizer_id: int


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[Dict] = None
    date: Optional[date] = None
    max_participants: Optional[int] = None
    price: Optional[float] = None
    image: Optional[str] = None


class EventResponse(EventBase):
    id: int
    organizer_id: int
    created_at: datetime


class RegistrationBase(BaseModel):
    event_id: int
    user_id: int
    status: int


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationResponse(RegistrationBase):
    id: int
    created_at: datetime


class FavouriteEventBase(BaseModel):
    user_id: int
    event_id: int


class FavouriteEventCreate(FavouriteEventBase):
    pass


class FavouriteEventResponse(FavouriteEventBase):
    id: int
    created_at: datetime


class FavouriteOrganizerBase(BaseModel):
    user_id: int
    organizer_id: int


class FavouriteOrganizerCreate(FavouriteOrganizerBase):
    pass


class FavouriteOrganizerResponse(FavouriteOrganizerBase):
    id: int
    created_at: datetime


class EventCategoryBase(BaseModel):
    event_id: int
    category_id: int


class EventCategoryCreate(EventCategoryBase):
    pass


class EventCategoryResponse(EventCategoryBase):
    id: int


class UserCategoryBase(BaseModel):
    user_id: int
    category_id: int


class UserCategoryCreate(UserCategoryBase):
    pass


class UserCategoryResponse(UserCategoryBase):
    id: int


class NotificationTypeBase(BaseModel):
    type: str
    description: Optional[str] = None


class NotificationTypeResponse(NotificationTypeBase):
    id: int


class NotificationBase(BaseModel):
    user_id: int
    type: int
    content: str
    is_read: bool = False


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
