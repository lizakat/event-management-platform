from datetime import datetime
from backend.crud import get_user_with_relations
from backend.models import User, RegistrationStatus
from backend.schemas import UserProfileData
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import database, schemas, crud

def get_user_statistics(registrations: list) -> dict:
    if not registrations:
        return {
            "events_visited": 0,
            "last_visit": "Нет данных",
            "statuses": {}
        }

    status_counts = {
        status.name: sum(1 for reg in registrations if reg.status.name == status.name)
        for status in RegistrationStatus.query.all()
    }

    return {
        "events_visited": len(registrations),
        "last_visit": max(reg.created_at for reg in registrations).strftime("%d.%m.%Y"),
        "statuses": status_counts
    }


def get_profile_data(user: User, db: Session = Depends(database.get_db)) -> UserProfileData:
    """Формирует данные для профиля пользователя."""
    user_with_relations = get_user_with_relations(db, user.id)

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
        "statistics": get_user_statistics(user_with_relations.registrations),
        "favorite_tags": [
            uc.category.name for uc in user_with_relations.user_categories
        ]
    }