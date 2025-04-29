import secrets
from sqlalchemy.orm import Session
from backend import crud
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from backend.config import settings

def generate_verification_code(db: Session, email: str):
    code = str(secrets.randbelow(900000) + 100000)  # 6-значный код
    crud.save_verification_code(db, email, code)
    return code

def validate_verification_code(db: Session, email: str, code: str):
    db_code = crud.get_verification_code(db, email)
    return db_code and db_code.code == code


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


from jose import jwt
from datetime import datetime, timedelta

def decode_token(token: str, secret_key: str, algorithm: str):

    return jwt.decode(token, secret_key, algorithms=[algorithm])