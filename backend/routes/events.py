from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, status
from backend.crud import get_event, create_event, save_uploaded_file
from backend.dependencies import get_current_user
from backend.models import User, Category, UserCategory, Event, Registration, RegistrationStatus
from sqlalchemy.orm import Session
from backend import database, schemas, crud, models
from backend.templates import templates
from backend.dependencies import get_current_organizer


router = APIRouter()


@router.get("/event/{event_id}")
async def show_event(
        request: Request,
        event_id: int,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    event = get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    is_registered = any(
        reg.user_id == current_user.id
        for reg in event.registrations
    ) if current_user else False

    is_favourite = crud.is_event_in_favourites(db, current_user.id, event_id) if current_user else False
    print(event.image)
    return templates.TemplateResponse(
        "event-page.html",
        {
            "request": request,
            "event": event,
            "current_user": current_user,
            "is_registered": is_registered,
            "is_favourite": is_favourite,
            "crud": crud
        }
    )


@router.get("/create-event")
async def show_create_event_form(
        request: Request,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    all_categories = db.query(Category).all()
    return templates.TemplateResponse(
        "create-event.html",
        {
            "request": request,
            "all_categories": all_categories,
            "current_user": current_user
        }
    )

@router.post("/create-event")
async def handle_create_event(
        request: Request,
        title: str = Form(...),
        description: str = Form(None),
        date: str = Form(...),
        time: str = Form(...),
        location: str = Form(None),
        max_participants: int = Form(None),
        price: float = Form(None),
        image: UploadFile = File(None),
        categories: list[str] = Form([]),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    # Проверка авторизации и роли
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    if current_user.role_id != 1:  # Проверяем, что пользователь организатор (role_id=1)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только организаторы могут создавать мероприятия"
        )

    try:
        event_data = {
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "location": location,  # Преобразуем в JSON
            "max_participants": max_participants,
            "price": price,
            "image": image,
            "categories": categories
        }

        # Преобразование даты и времени
        #event_data["date"] = datetime.strptime(date, "%Y-%m-%d").date()
       # event_data["time"] = datetime.strptime(time, "%H:%M").time()

        # Создаем событие
        event = create_event(db, event_data, current_user.id)
        return RedirectResponse(f"/events/event/{event.id}", status_code=303)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка формата данных: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")



@router.get("/edit-event/{event_id}")
async def show_edit_event_form(
        request: Request,
        event_id: int,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_organizer)
):
    # Проверяем, что пользователь авторизован
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    # Получаем мероприятие
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    # Проверяем, что пользователь - организатор этого мероприятия
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования")

    # Получаем все категории
    all_categories = db.query(models.Category).all()

    return templates.TemplateResponse(
        "edit-event.html",
        {
            "request": request,
            "event": event,
            "all_categories": all_categories,
            "current_user": current_user
        }
    )


@router.post("/edit-event/{event_id}")
async def handle_edit_event(
        request: Request,
        event_id: int,
        title: str = Form(...),
        description: str = Form(None),
        date: str = Form(...),
        time: str = Form(...),
        location: str = Form(None),
        max_participants: int = Form(None),
        price: float = Form(None),
        image: UploadFile = File(None),
        categories: List[str] = Form([]),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_organizer)
):
    # Проверяем авторизацию
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    # Получаем мероприятие
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    print("h1")
    # Проверяем права
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования")
    print("h2")
    try:
        # Обновляем данные
        event.title = title
        event.description = description
        event.date = datetime.strptime(date, "%Y-%m-%d").date()
        event.time = datetime.strptime(time, "%H:%M").time()
        event.location = {"address": location} if location else None
        event.max_participants = max_participants
        event.price = price
        print("h3")
        # Обновляем изображение, если загружено новое
        if image:
            event.image = save_uploaded_file(image)

        # Обновляем категории
        # Сначала удаляем все текущие категории
        db.query(models.EventCategory).filter(models.EventCategory.event_id == event_id).delete()
        print("h4")
        # Добавляем новые категории
        for category_id in categories:
            db_category = models.EventCategory(event_id=event_id, category_id=int(category_id))
            db.add(db_category)
        print("h5")
        db.commit()

        return RedirectResponse(f"/events/event/{event_id}", status_code=303)

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка формата данных: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.delete("/delete-event/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_organizer)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    db.delete(event)
    db.commit()
    return {"message": "Мероприятие удалено"}


@router.post("/event/{event_id}/favourite")
async def toggle_favourite(
        event_id: int,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    is_favourite = crud.is_event_in_favourites(db, current_user.id, event_id)

    if is_favourite:
        crud.remove_from_favourites(db, current_user.id, event_id)
        return {"status": "removed"}
    else:
        crud.add_to_favourites(db, current_user.id, event_id)
        return {"status": "added"}

@router.post("/event/{event_id}/register")
async def register_for_event(
        event_id: int,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is already registered
    existing_registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()

    if existing_registration:
        raise HTTPException(status_code=400, detail="Already registered")

    # Create new registration with "Confirmed" status (status_id=2)
    new_registration = Registration(
        user_id=current_user.id,
        event_id=event_id,
        status_id=1  # "Confirmed" status
    )

    db.add(new_registration)
    db.commit()

    return {"status": "success", "message": "Registration successful"}


@router.post("/event/{event_id}/cancel-registration")
async def cancel_registration(
        event_id: int,
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    registration = db.query(Registration).filter(
        Registration.user_id == current_user.id,
        Registration.event_id == event_id
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Simply delete the registration record
    db.delete(registration)
    db.commit()

    return {"status": "success", "message": "Registration cancelled and removed"}