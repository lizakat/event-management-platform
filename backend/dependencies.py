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
from jose import jwt
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            raise credentials_exception
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
        email = payload.get("sub")
        print(f"Email {email}")
        if email is None:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception




async def get_current_organizer(
    current_user: User = Depends(get_current_user)
):
    print(current_user.role_id)
    if current_user.role_id != 1:  # Проверяем, что role_id = 1 (админ/организатор)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут создавать мероприятия"
        )
    return current_user