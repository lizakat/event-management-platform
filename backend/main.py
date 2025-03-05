from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
from backend import models, schemas, crud
from backend.database import engine, SessionLocal
from sqlalchemy.orm import Session

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


@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)
