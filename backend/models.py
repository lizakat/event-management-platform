from sqlalchemy import Column, Integer, Text, Date, JSON, TIMESTAMP, ForeignKey, Boolean, Float, func
from sqlalchemy.orm import relationship
from backend.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role", cascade="all, delete")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)

    event_categories = relationship("EventCategory", back_populates="category", cascade="all, delete")
    user_categories = relationship("UserCategory", back_populates="category", cascade="all, delete")

class RegistrationStatus(Base):
    __tablename__ = "registration_statuses"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Text, nullable=False, unique=True)

    registrations = relationship("Registration", back_populates="status", cascade="all, delete")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text)
    google_id = Column(Text)
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    avatar = Column(Text)
    birthdate = Column(Date)
    location = Column(JSON)
    phone = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role", back_populates="users")
    registrations = relationship("Registration", back_populates="user", cascade="all, delete")
    favourite_events = relationship("FavouriteEvent", back_populates="user", cascade="all, delete")
    favourite_organizers = relationship("FavouriteOrganizer", foreign_keys="[FavouriteOrganizer.user_id]", back_populates="user", cascade="all, delete")
    favourite_organizers_as_organizer = relationship("FavouriteOrganizer", foreign_keys="[FavouriteOrganizer.organizer_id]", back_populates="favourite_organizers_as_organizer", cascade="all, delete")
    user_categories = relationship("UserCategory", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")
    
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    location = Column(JSON)
    date = Column(Date, nullable=False)
    max_participants = Column(Integer)
    price = Column(Float)
    image = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    organizer = relationship("User")
    categories = relationship("EventCategory", back_populates="event", cascade="all, delete")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete")
    favourite_events = relationship("FavouriteEvent", back_populates="event", cascade="all, delete")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('registration_statuses.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    status = relationship("RegistrationStatus", back_populates="registrations")

class FavouriteEvent(Base):
    __tablename__ = "favourite_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="favourite_events")
    event = relationship("Event", back_populates="favourite_events")

class FavouriteOrganizer(Base):
    __tablename__ = "favourite_organizers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    organizer_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="favourite_organizers")
    favourite_organizers_as_organizer = relationship("User", foreign_keys=[organizer_id], back_populates="favourite_organizers_as_organizer")

class EventCategory(Base):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    event = relationship("Event", back_populates="categories")
    category = relationship("Category", back_populates="event_categories")

class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="user_categories")
    category = relationship("Category", back_populates="user_categories")

class NotificationType(Base):
    __tablename__ = "notification_types"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(Text, nullable=False, unique=True)
    description = Column(Text)

    notifications = relationship("Notification", back_populates="notification_type", cascade="all, delete")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    notification_type_id = Column(Integer, ForeignKey('notification_types.id'), nullable=False)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="notifications")
    notification_type = relationship("NotificationType", back_populates="notifications")

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    code = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(Text, nullable=False, unique=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")