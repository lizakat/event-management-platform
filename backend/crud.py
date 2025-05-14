import uuid
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
from sqlalchemy.orm import Session, joinedload
from backend import models, schemas
from backend.models import VerificationCode, User, Registration, UserCategory, Event, EventCategory, FavouriteOrganizer
import os
from datetime import datetime
from fastapi import UploadFile



def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        password=hashed_password,
        name=user.name,
        surname=user.surname,
        google_id=user.google_id,
        role_id=user.role_id,
        avatar=user.avatar,
        birthdate=user.birthdate,
        location=user.location,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def save_verification_code(db: Session, email: str, code: str):
    db_code = VerificationCode(email=email, code=code)
    db.add(db_code)
    db.commit()

def get_verification_code(db: Session, email: str):
    return db.query(VerificationCode).filter(VerificationCode.email == email).first()

def delete_expired_codes(db: Session):
    expiration_time = datetime.utcnow() - timedelta(minutes=5)
    db.query(VerificationCode).filter(VerificationCode.created_at < expiration_time).delete()
    db.commit()

def get_user_with_relations(db: Session, user_id: int) -> User:
    """Получает пользователя со всеми связанными данными."""
    return db.query(User) \
        .options(
        joinedload(User.registrations).joinedload(Registration.event),
        joinedload(User.registrations).joinedload(Registration.status),
        joinedload(User.user_categories).joinedload(UserCategory.category)
    ) \
        .filter(User.id == user_id) \
        .first()



def get_event(db: Session, event_id: int):
    return db.query(Event).options(
        joinedload(Event.organizer),
        joinedload(Event.categories).joinedload(EventCategory.category),
        joinedload(Event.registrations)
    ).filter(Event.id == event_id).first()


def create_event(db: Session, event_data: dict, organizer_id: int):
    try:
        # Преобразуем дату и время
        event_date = datetime.strptime(event_data['date'], "%Y-%m-%d").date()
        event_time = datetime.strptime(event_data['time'], "%H:%M").time()

        # Создаем событие
        db_event = Event(
            title=event_data['title'],
            description=event_data['description'],
            date=event_date,
            time=event_time,
            location=event_data['location'],
            max_participants=event_data.get('max_participants'),
            price=event_data.get('price'),
            organizer_id=organizer_id,
            image=save_uploaded_file(event_data['image']) if event_data.get('image') else None
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # Добавляем категории
        for category_id in event_data.get('categories', []):
            db_category = EventCategory(event_id=db_event.id, category_id=int(category_id))
            db.add(db_category)

        db.commit()
        return db_event
    except Exception as e:
        db.rollback()
        raise


def add_to_favourites(db: Session, user_id: int, event_id: int):
    # Проверяем, не добавлено ли уже в избранное
    existing = db.query(models.FavouriteEvent).filter(
        models.FavouriteEvent.user_id == user_id,
        models.FavouriteEvent.event_id == event_id
    ).first()

    if existing:
        return None

    db_fav = models.FavouriteEvent(
        user_id=user_id,
        event_id=event_id
    )
    db.add(db_fav)
    db.commit()
    db.refresh(db_fav)
    return db_fav


def remove_from_favourites(db: Session, user_id: int, event_id: int):
    db.query(models.FavouriteEvent).filter(
        models.FavouriteEvent.user_id == user_id,
        models.FavouriteEvent.event_id == event_id
    ).delete()
    db.commit()


def get_user_favourites(db: Session, user_id: int):
    return db.query(models.FavouriteEvent).filter(
        models.FavouriteEvent.user_id == user_id
    ).all()


def is_event_in_favourites(db: Session, user_id: int, event_id: int):
    return db.query(models.FavouriteEvent).filter(
        models.FavouriteEvent.user_id == user_id,
        models.FavouriteEvent.event_id == event_id
    ).first() is not None

def get_event_org_name(db: Session, event_id: int):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event:
        organizer = db.query(models.User).filter(models.User.id == event.organizer_id).first()
        if organizer:
            return f"{organizer.name} {organizer.surname}"
    return None


def save_uploaded_file(upload_file: UploadFile) -> str:
    # Создаем уникальное имя файла
    file_ext = os.path.splitext(upload_file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"

    # Путь для сохранения
    save_path = os.path.join("/static/uploads", file_name)

    # Создаем директорию, если её нет
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Сохраняем файл
    with open(save_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    print("файл сохранен")
    return f"/static/uploads/{file_name}"

def get_organizer_with_stats(db: Session, organizer_id: int):
    """Получаем организатора с расширенной статистикой"""
    organizer = db.query(User).options(
        joinedload(User.favourite_organizers_as_organizer)
    ).filter(User.id == organizer_id).first()

    if not organizer:
        return None

    # Получаем статистику
    events_count = db.query(Event).filter(Event.organizer_id == organizer_id).count()
    followers_count = db.query(FavouriteOrganizer).filter(
        FavouriteOrganizer.organizer_id == organizer_id
    ).count()

    return {
        "id": organizer.id,
        "name": organizer.name,
        "surname": organizer.surname,
        "email": organizer.email,
        "avatar": organizer.avatar or "/static/images/avatar_1.jfif",
        "events_count": events_count,
        "followers_count": followers_count,
        "is_followed": any(f.user_id == organizer_id for f in organizer.favourite_organizers_as_organizer)
    }


def toggle_favorite_organizer(db: Session, user_id: int, organizer_id: int):
    """Переключаем статус организатора в избранном с проверками"""
    # Проверяем, что пользователь не пытается добавить себя
    if user_id == organizer_id:
        raise ValueError("Нельзя добавить себя в избранное")

    # Проверяем существование организатора
    organizer = db.query(User).filter(User.id == organizer_id).first()
    if not organizer:
        raise ValueError("Организатор не найден")

    existing = db.query(FavouriteOrganizer).filter(
        FavouriteOrganizer.user_id == user_id,
        FavouriteOrganizer.organizer_id == organizer_id
    ).first()

    try:
        if existing:
            db.delete(existing)
            action = "removed"
        else:
            db_fav = FavouriteOrganizer(
                user_id=user_id,
                organizer_id=organizer_id,
                created_at=datetime.utcnow()
            )
            db.add(db_fav)
            action = "added"

        db.commit()

        # Обновляем счетчик подписчиков
        followers_count = db.query(FavouriteOrganizer).filter(
            FavouriteOrganizer.organizer_id == organizer_id
        ).count()

        return {
            "status": action,
            "followers_count": followers_count,
            "is_followed": action == "added"
        }

    except Exception as e:
        db.rollback()
        raise ValueError(f"Ошибка при обновлении избранного: {str(e)}")