from fastapi import APIRouter, Request, Depends, HTTPException, Response, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session, joinedload
from backend import database, schemas, crud, models
from backend.config import settings
from backend import schemas
from backend.dependencies import get_current_user
from backend.models import Registration, UserCategory, User, RegistrationStatus, FavouriteOrganizer
from backend.schemas import UserBase
from backend.services import users
from backend.services.auth import require_user_or_redirect
from backend.services.events import prepare_event_data
from backend.templates import templates
from sqlalchemy.orm import Session
from backend import database
from backend.models import Event, FavouriteEvent
from math import ceil
from datetime import datetime

now = datetime.now()
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
        org_name=crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": is_favourite,
            "org_name": org_name
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
async def read_favourite_events(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5

    # Получаем избранные события пользователя через связь FavouriteEvent
    query = db.query(Event).join(
        FavouriteEvent,
        FavouriteEvent.event_id == Event.id
    ).filter(
        FavouriteEvent.user_id == current_user.id
    )

    total_events = query.count()
    total_pages = ceil(total_events / per_page)

    events = query.order_by(Event.date.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()


    events_with_favourites = []
    for event in events:
        org_name = crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": True,
            "org_name": org_name
        })

    return templates.TemplateResponse(
        "favourite-events.html",
        {
            "request": request,
            "title": "Избранные события",
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "crud": crud
        }
    )


@router.get("/favourite-org")
async def read_favourite_organizers(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5

    # Получаем избранных организаторов пользователя
    query = db.query(User).join(
        FavouriteOrganizer,
        FavouriteOrganizer.organizer_id == User.id
    ).filter(
        FavouriteOrganizer.user_id == current_user.id
    )

    total_organizers = query.count()
    total_pages = ceil(total_organizers / per_page)

    organizers = query.order_by(User.name.asc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    # Подготавливаем данные организаторов
    organizers_data = []
    for organizer in organizers:
        organizer_data = crud.get_organizer_with_stats(db, organizer.id)
        if organizer_data:
            organizers_data.append({
                "organizer": organizer_data,
                "is_favorite": True
            })
    return templates.TemplateResponse(
        "favourite-org.html",  # Убедитесь, что у вас есть этот шаблон
        {
            "request": request,
            "title": "Избранные организаторы",
            "organizers": organizers_data,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user
        }
    )


@router.get("/user-registrations")
async def read_user_registrations(request: Request):
    return templates.TemplateResponse("user-registrations.html", {"request": request, "title": "Мои регистрации"})


@router.get("/org-events")
async def read_org_events(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5
    today = datetime.now().date()
    
    # Фильтруем по организатору и дате (>= сегодня)
    query = db.query(Event).filter(
        Event.organizer_id == current_user.id,
        (Event.date > now.date()) | 
        ((Event.date == now.date()) & (Event.time > now.time()))
    )
    
    total_events = query.count()
    total_pages = ceil(total_events / per_page)
    
    events = query.order_by(Event.date.asc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    events_with_favourites = []
    for event in events:
        is_favourite = crud.is_event_in_favourites(db, current_user.id, event.id)
        org_name=crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": is_favourite,
            "org_name": org_name
        })

    return templates.TemplateResponse(
        "org-events.html",
        {
            "request": request,
            "title": "Мои события",
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "crud": crud
        }
    )


@router.get("/passed-events")
async def read_org_passed_events(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5
    today = datetime.now().date()
    
    query = db.query(Event).filter(
        Event.organizer_id == current_user.id,
        (Event.date < now.date()) | 
        ((Event.date == now.date()) & (Event.time <= now.time()))
    )
    
    total_events = query.count()
    total_pages = ceil(total_events / per_page)
    
    events = query.order_by(Event.date.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    events_with_favourites = []
    for event in events:
        is_favourite = crud.is_event_in_favourites(db, current_user.id, event.id)
        org_name=crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": is_favourite,
            "org_name": org_name
        })

    return templates.TemplateResponse(
        "org-passed-events.html",
        {
            "request": request,
            "title": "Прошедшие события",
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "crud": crud
        }
    )


@router.get("/active-registrations")
async def active_registrations(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5
    today = datetime.now().date()

    query = db.query(Event).join(Registration).filter(
        Registration.user_id == current_user.id,
        Event.date >= today
    )

    total_events = query.count()
    total_pages = ceil(total_events / per_page)

    events = query.order_by(Event.date.asc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    events_with_favourites = []
    for event in events:
        is_favourite = crud.is_event_in_favourites(db, current_user.id, event.id)
        org_name=crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": is_favourite,
            "org_name": org_name
        })
    return templates.TemplateResponse(
        "user-registrations.html",
        {
            "request": request,
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "active_tab": "active"  # Для подсветки активной кнопки
        }
    )


@router.get("/passed-registrations")
async def passed_registrations(
        request: Request,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5
    today = datetime.now().date()

    query = db.query(Event).join(Registration).filter(
        Registration.user_id == current_user.id,
        Event.date < today
    )

    total_events = query.count()
    total_pages = ceil(total_events / per_page)

    events = query.order_by(Event.date.desc()) \
        .offset((page - 1) * per_page) \
        .limit(per_page) \
        .all()

    events_with_favourites = []
    for event in events:
        is_favourite = crud.is_event_in_favourites(db, current_user.id, event.id)
        org_name=crud.get_event_org_name(db, event.id)
        events_with_favourites.append({
            "event": prepare_event_data(event),
            "is_favourite": is_favourite,
            "org_name": org_name
        })

    return templates.TemplateResponse(
        "user-registrations.html",
        {
            "request": request,
            "events": events_with_favourites,
            "current_page": page,
            "total_pages": total_pages,
            "current_user": current_user,
            "active_tab": "passed"  # Для подсветки активной кнопки
        }
    )


@router.get("/organizer/{organizer_id}")
async def show_organizer_events(
        request: Request,
        organizer_id: int,
        page: int = Query(1, ge=1),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    per_page = 5

    # Получаем данные организатора
    organizer = crud.get_organizer_with_stats(db, organizer_id)
    if not organizer:
        raise HTTPException(status_code=404, detail="Organizer not found")

    # Проверяем, в избранном ли организатор
    is_favorite = db.query(models.FavouriteOrganizer).filter(
        models.FavouriteOrganizer.user_id == current_user.id,
        models.FavouriteOrganizer.organizer_id == organizer_id
    ).first() is not None

    # Получаем события организатора с пагинацией
    query = db.query(models.Event).filter(
        models.Event.organizer_id == organizer_id
    )
    total_events = query.count()
    events = query.order_by(models.Event.date.desc()) \
                 .offset((page - 1) * per_page) \
                 .limit(per_page) \
                 .all()

    total_pages = ceil(total_events / per_page)

    # Подготавливаем данные для шаблона
    events_data = []
    for event in events:
        event_data = prepare_event_data(event)
        event_data['is_favourite'] = crud.is_event_in_favourites(db, current_user.id, event.id)
        events_data.append(event_data)

    return templates.TemplateResponse(
        "organizer.html",
        {
            "request": request,
            "current_page": page,
            "total_pages": total_pages,
            "organizer": organizer,
            "is_favorite": is_favorite,
            "events": events_data,
            "current_user": current_user
        }
    )


@router.post("/organizer/{organizer_id}/favourite")
async def toggle_favorite_organizer(
    organizer_id: int,
    db: Session = Depends(database.get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = crud.toggle_favorite_organizer(db, current_user.id, organizer_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")