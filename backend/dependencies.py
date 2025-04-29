from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError
from jose.exceptions import (
    JWTError,
    ExpiredSignatureError,
    JWTClaimsError,
    JWTClaimsError,
    JWSError,
    JWTError
)
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User
from backend.services.auth import decode_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials0",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception1 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials1",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception2 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials2",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception3 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials3",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Пробуем получить токен из куки
    token = request.cookies.get("access_token")
    if not token:
        # 2. Если нет в куках, пробуем из заголовка
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            raise credentials_exception1
    if token.startswith("Bearer "):
        token = token[7:]  # Обрезаем первые 7 символов

    try:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except ExpiredSignatureError:
            print("Ошибка: Токен просрочен")
            raise HTTPException(
                status_code=401,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except JWTError as e:  # Ловит все остальные ошибки JWT
            print(f"Ошибка верификации токена: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        print(f"Payload {payload}")
        email = payload.get("sub")
        print(f"Email {email}")
        if email is None:
            raise credentials_exception2



        # 4. Ищем пользователя в БД
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception3

        return user

    except JWTError:
        raise credentials_exception



from jose import jwt
from datetime import datetime, timedelta

def decode_token(token: str, secret_key: str, algorithm: str):
    """Декодирует JWT токен с обработкой ошибок"""
    return jwt.decode(token, secret_key, algorithms=[algorithm])