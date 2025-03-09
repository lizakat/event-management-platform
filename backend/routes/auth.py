import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import database, schemas, crud

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


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email не найден")

    if not crud.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    return {"message": "Успешный вход", "user_id": db_user.id}


@router.get("/check-email")
async def check_email(email: str, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email)
    if user:
        return {"exists": True}
    return {"exists": False}