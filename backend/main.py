import secrets
from typing import Dict

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from pydantic import BaseModel

from backend import models, schemas, crud
from backend.database import engine, SessionLocal
from sqlalchemy.orm import Session

from backend.schemas import UserLogin

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
app.mount("/public", StaticFiles(directory=os.path.join(FRONTEND_DIR, "public")), name="public")

templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("register_st1.html", {"request": request, "title": "Регистрация"})

@app.get("/register")
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})


@app.get("/forgot-password")
async def read_register(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request, "title": "Восстановление пароля"})

@app.get("/new-password")
async def read_register(request: Request):
    return templates.TemplateResponse("new-password.html", {"request": request, "title": "Восстановление пароля"})

@app.get("/notification-password")
async def read_register(request: Request):
    return templates.TemplateResponse("notification-password.html", {"request": request, "title": "Восстановление пароля"})

@app.get("/login", name="login")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход", "current_page": "login"})

@app.get("/main-page")
async def read_root(request: Request):
    return templates.TemplateResponse("main-page.html", {"request": request, "title": "Главная"})

@app.get("/profile", name="profile")
async def read_root(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, 'title': "Аккаунт", "current_page": "profile"})


@app.get("/create-event")
async def read_register(request: Request):
    return templates.TemplateResponse("create-event.html", {"request": request, "title": "Создание события"})

@app.get("/edit-event")
async def read_register(request: Request):
    return templates.TemplateResponse("edit-event.html", {"request": request, "title": "Изменить событие"})

@app.get("/edit-profile")
async def read_root(request: Request):
    return templates.TemplateResponse("edit-profile.html", {"request": request, "title": "Редактировать профиль"})

@app.get("/event-page")
async def read_root(request: Request):
    return templates.TemplateResponse("event-page.html", {"request": request, "title": "Событие ххх"})

@app.get("/favourite-events")
async def read_root(request: Request):
    return templates.TemplateResponse("favourite-events.html", {"request": request, "title": "Любимые события"})

@app.get("/user-registrations")
async def read_root(request: Request):
    return templates.TemplateResponse("user-registrations.html", {"request": request, "title": "Мои регистрации"})



@app.get("/check-email")
async def check_email(email: str, db: Session = Depends(get_db)):
    user_exists = crud.check_if_email_exists(db, email)
    return {"exists": user_exists}

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.check_if_email_exists(db, user.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован")
    return crud.create_user(db=db, user=user)


# Хранение кодов в памяти (в реальном приложении используйте базу данных)
codes_db: Dict[str, str] = {}  # email -> code

# Модели данных
class GenerateCodeRequest(BaseModel):
    email: str

class ValidateCodeRequest(BaseModel):
    email: str
    code: str

class CheckEmailRequest(BaseModel):
    email: str

# Эндпоинт для генерации кода
@app.post("/generate-code")
async def generate_code(request: GenerateCodeRequest):
    email = request.email

    # Генерация 6-значного кода
    code = secrets.randbelow(900000) + 100000  # Генерация кода от 100000 до 999999
    code = str(code)

    # Сохраняем код в памяти
    codes_db[email] = code

    # В реальном приложении отправьте код по email
    print(f"Код для {email}: {code}")

    return {"success": True, "message": "Код отправлен"}

# Эндпоинт для проверки кода
@app.post("/validate-code")
async def validate_code(request: ValidateCodeRequest):
    email = request.email
    code = request.code
    print(request)

    # Получаем сохраненный код
    saved_code = codes_db.get(email)
    print(email, code)
    if saved_code and saved_code == code:
        return {"valid": True}
    else:
        return {"valid": False}

@app.post("/login")
async def login(request: UserLogin):
    email = request.email
    password = request.password

    # Проверяем, существует ли пользователь
    user = db_user.get(email)
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email не найден")

    # Проверяем пароль
    if user["password"] != password:  # В реальном приложении используйте хеширование и проверку хешей
        raise HTTPException(status_code=400, detail="Неверный пароль")

    # Если всё верно, возвращаем успешный ответ
    return {"success": True, "message": "Вход выполнен успешно"}