import secrets
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import JWTError, jwt

from backend import database, schemas, crud
from backend.config import settings

router = APIRouter()


@router.post("/generate-code")
def generate_code(request: schemas.GenerateCodeRequest, db: Session = Depends(database.get_db)):
    email = request.email
    code = str(secrets.randbelow(900000) + 100000)
    crud.save_verification_code(db, email, code)

    print(f"Код для {email}: {code}")

    return {"success": True, "message": "Код отправлен"}


@router.post("/validate-code")
def validate_code(request: schemas.ValidateCodeRequest, db: Session = Depends(database.get_db)):
    email, code = request.email, request.code
    db_code = crud.get_verification_code(db, email)

    if db_code and db_code.code == code:
        return {"valid": True}

    return {"valid": False}


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
    return crud.create_user(db=db, user=user)



@router.get("/check-email")
async def check_email(email: str, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email)
    if user:
        return {"exists": True}
    return {"exists": False}


@router.post("/login")
def login(
        response: Response,
        user: schemas.UserLogin,
        db: Session = Depends(database.get_db)
):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email не найден")

    if not crud.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    # Создаем JWT токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )

    # Устанавливаем HTTP-only куку
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,  # Для HTTPS
        samesite="lax"
    )

    return {
        "message": "Успешный вход",
        "user_id": db_user.id,
        "access_token": access_token,  # Для localStorage
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Успешный выход"}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt