from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Date, JSON, TIMESTAMP, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)

    event_categories = relationship("EventCategory", back_populates="category")

class RegistrationStatus(Base):
    __tablename__ = "registration_statuses"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Text, nullable=False, unique=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    password = Column(Text)
    google_id = Column(Text, index=True)
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    avatar = Column(Text)
    birthdate = Column(Date)
    location = Column(JSON)
    phone = Column(Text)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    role = relationship("Role", back_populates="users")
    registrations = relationship("Registration", back_populates="user")
    favourite_events = relationship("FavouriteEvent", back_populates="user")
    favourite_organizers = relationship("FavouriteOrganizer", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey('users.id'))
    title = Column(Text, nullable=False)
    description = Column(Text)
    location = Column(JSON)
    date = Column(Date, nullable=False)
    max_participants = Column(Integer)
    price = Column(Float)
    image = Column(Text)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    organizer = relationship("User")
    categories = relationship("EventCategory", back_populates="event")
    registrations = relationship("Registration", back_populates="event")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Integer, ForeignKey('registration_statuses.id'))
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")

class FavouriteEvent(Base):
    __tablename__ = "favourite_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    user = relationship("User", back_populates="favourite_events")
    event = relationship("Event", back_populates="favourite_events")

class FavouriteOrganizer(Base):
    __tablename__ = "favourite_organizers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    organizer_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    user = relationship("User", back_populates="favourite_organizers")
    organizer = relationship("User", back_populates="favourite_organizers")

class EventCategory(Base):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    event = relationship("Event", back_populates="categories")
    category = relationship("Category", back_populates="event_categories")

class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

class NotificationType(Base):
    __tablename__ = "notification_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Text, nullable=False, unique=True)
    description = Column(Text)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(Integer, ForeignKey('notification_types.id'))
    content = Column(Text)
    is_read = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')