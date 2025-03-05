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



def check_if_email_exists(db: Session, email: str) -> bool:
    user = db.query(models.User).filter(models.User.email == email).first()
    return user is not None