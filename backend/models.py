from sqlalchemy import Column, Integer, String, Text, Date, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    description = Column(Text)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text)
    google_id = Column(Text)
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    avatar = Column(Text)
    birthdate = Column(Date)
    location = Column(JSON)
    phone = Column(Text)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    role = relationship("Role")

