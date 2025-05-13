from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from backend import database
from backend.crud import get_user_with_relations
from backend.models import User, RegistrationStatus


def get_user_statistics(db: Session, registrations: list) -> dict:
    if not registrations:
        return {
            "events_visited": 0,
            "last_visit": "Нет данных"
        }
    last_visit = max(reg.event.date for reg in registrations if reg.event.date < datetime.now().date()) \
        if any(reg.event.date < datetime.now().date() for reg in registrations) \
        else None

    past_events_count = sum(1 for reg in registrations if reg.event.date < datetime.now().date())

    return {
        "events_visited": past_events_count,
        "last_visit": last_visit.strftime("%d.%m.%Y") if last_visit else "Нет данных"
    }

def get_profile_data(user: User, db: Session) -> dict:
    """Формирует данные для профиля пользователя."""
    user_with_relations = get_user_with_relations(db, user.id)

    # Передаем db в get_user_statistics
    statistics = get_user_statistics(db, user_with_relations.registrations)

    return {
        "name": user_with_relations.name,
        "surname": user_with_relations.surname,
        "email": user_with_relations.email,
        "phone": user_with_relations.phone or "Не указан",
        "role_id": user_with_relations.role_id,
        "location": user_with_relations.location or "Не указан",
        "birthdate": user_with_relations.birthdate.strftime("%d.%m.%Y")
        if user_with_relations.birthdate
        else "Не указана",
        "statistics": statistics,
        "favorite_tags": [
            uc.category.name for uc in user_with_relations.user_categories
        ]
    }