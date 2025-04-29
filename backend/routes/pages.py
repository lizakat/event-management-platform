from fastapi import APIRouter, Request, Depends, HTTPException, Response, status

from sqlalchemy.orm import Session, joinedload
from backend import database, schemas, crud
from backend.config import settings
from backend import schemas
from backend.dependencies import get_current_user
from backend.models import Registration, UserCategory, User, RegistrationStatus
from backend.schemas import UserBase
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
async def read_main_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("main-page.html", {"request": request, "title": "Главная"})



@router.get("/profile", name="profile")
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        # Явно загружаем связанные данные одним запросом
        user_with_relations = db.query(User)\
            .options(
                joinedload(User.registrations).joinedload(Registration.event),
                joinedload(User.registrations).joinedload(Registration.status),
                joinedload(User.user_categories).joinedload(UserCategory.category)
            )\
            .filter(User.id == current_user.id)\
            .first()

        # Формируем данные для профиля
        profile_data = {
            "request": request,
            "user": {
                "name": user_with_relations.name,
                "surname": user_with_relations.surname,
                "email": user_with_relations.email,
                "phone": user_with_relations.phone or "Не указан",
                "location": user_with_relations.location or "Не указан",
                "birthdate": user_with_relations.birthdate.strftime("%d.%m.%Y")
                    if user_with_relations.birthdate
                    else "Не указана",
                "statistics": {
                    "events_visited": len(user_with_relations.registrations),
                    "last_visit": max(
                        [reg.created_at for reg in user_with_relations.registrations],
                        default=None
                    ).strftime("%d.%m.%Y") if user_with_relations.registrations else "Нет данных",
                    "statuses": {
                        status.name: sum(1 for reg in user_with_relations.registrations
                                      if reg.status.name == status.name)
                        for status in db.query(RegistrationStatus).all()
                    }
                },
                "favorite_tags": [
                    uc.category.name for uc in user_with_relations.user_categories
                ]
            }
        }
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,  # Обязательно!
                "title": "Аккаунт",
                "current_page": "profile",  # Для страницы профиля должно быть "profile"
                **profile_data  # Распаковываем ваши данные
            }
        )
    except Exception as e:
        print(f"Error rendering profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

@router.get("/favourite-org")
async def read_favourite_org(request: Request):
    return templates.TemplateResponse("favourite-org.html", {"request": request, "title": "Любимые организаторы"})

@router.get("/user-registrations")
async def read_user_registrations(request: Request):
    return templates.TemplateResponse("user-registrations.html", {"request": request, "title": "Мои регистрации"})
