from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.models import VerificationCode

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        password=hashed_password,
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


def save_verification_code(db: Session, email: str, code: str):
    db_code = VerificationCode(email=email, code=code)
    db.add(db_code)
    db.commit()

def get_verification_code(db: Session, email: str):
    return db.query(VerificationCode).filter(VerificationCode.email == email).first()

def delete_expired_codes(db: Session):
    expiration_time = datetime.utcnow() - timedelta(minutes=5)
    db.query(VerificationCode).filter(VerificationCode.created_at < expiration_time).delete()
    db.commit()