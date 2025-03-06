from fastapi import APIRouter, Request
from backend.templates import templates

router = APIRouter()

@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("register_st1.html", {"request": request, "title": "Регистрация"})

@router.get("/register")
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Регистрация"})

@router.get("/login", name="login")
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход", "current_page": "login"})

@router.get("/main-page")
async def read_main_page(request: Request):
    return templates.TemplateResponse("main-page.html", {"request": request, "title": "Главная"})

@router.get("/profile", name="profile")
async def read_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, "title": "Аккаунт", "current_page": "profile"})

@router.get("/create-event")
async def read_create_event(request: Request):
    return templates.TemplateResponse("create-event.html", {"request": request, "title": "Создание события"})

@router.get("/edit-event")
async def read_edit_event(request: Request):
    return templates.TemplateResponse("edit-event.html", {"request": request, "title": "Изменить событие"})

@router.get("/edit-profile")
async def read_edit_profile(request: Request):
    return templates.TemplateResponse("edit-profile.html", {"request": request, "title": "Редактировать профиль"})

@router.get("/event-page")
async def read_event_page(request: Request):
    return templates.TemplateResponse("event-page.html", {"request": request, "title": "Событие"})

@router.get("/favourite-events")
async def read_favourite_events(request: Request):
    return templates.TemplateResponse("favourite-events.html", {"request": request, "title": "Любимые события"})

@router.get("/user-registrations")
async def read_user_registrations(request: Request):
    return templates.TemplateResponse("user-registrations.html", {"request": request, "title": "Мои регистрации"})
