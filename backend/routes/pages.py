from fastapi import APIRouter, Request, Depends, HTTPException, Response, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session, joinedload
from backend import database, schemas, crud
from backend.config import settings
from backend import schemas
from backend.dependencies import get_current_user
from backend.models import Registration, UserCategory, User, RegistrationStatus
from backend.schemas import UserBase
from backend.services import users
from backend.services.auth import require_user_or_redirect
from backend.templates import templates
from sqlalchemy.orm import Session
from backend import database
from backend.models import Event
from math import ceil


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
async def read_main_page(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5
    total_events = db.query(Event).count()
    total_pages = ceil(total_events / per_page)

    events = db.query(Event) \
        .order_by(Event.date.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    # Добавляем информацию об избранном для каждого события
    events_with_favourites = []
    for event in events:
        is_favourite = crud.is_event_in_favourites(db, current_user.id, event.id) if current_user else False
        events_with_favourites.append({
            "event": event,
            "is_favourite": is_favourite
        })

    return templates.TemplateResponse(
        "main-page.html",
        {
            "request": request,
            "title": "Главная",
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "crud": crud
        }
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user = Depends(require_user_or_redirect),
    db: Session = Depends(database.get_db)
):
    if isinstance(user, RedirectResponse):
        return user

    try:
        profile_data = users.get_profile_data(user, db)
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "title": "Аккаунт",
            "current_page": "profile",
            "user": profile_data
        })
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
    return templates.TemplateResponse("edit-profile.html", {"request": request, "title": "Изменить профиль"})


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
