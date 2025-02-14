from sqlalchemy.orm import Session
from backend import models
from backend import schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password=user.password,
        name=user.name,
        surname=user.surname,
        google_id=user.google_id,
        role_id=user.role_id,
        avatar=user.avatar,
        birthdate=user.birthdate,
        location=user.location,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user