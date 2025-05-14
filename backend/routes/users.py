from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse

from backend.crud import save_uploaded_file
from backend.dependencies import get_current_user
from backend.models import User, Category, UserCategory
from sqlalchemy.orm import Session
from backend import database, schemas, crud
from backend.templates import templates


router = APIRouter()


@router.get("/edit-profile", name="edit-profile")
async def edit_profile_get(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(database.get_db)
):
    all_tags = db.query(Category).all()

    # Для отладки
    print(f"Найдено категорий: {len(all_tags)}")
    for tag in all_tags:
        print(tag.name)
    return templates.TemplateResponse(
        "edit-profile.html",
        {
            "request": request,
            "user": current_user,
            "all_tags": all_tags  # Убедитесь что передаёте переменную
        }
    )


@router.post("/edit-profile")
async def edit_profile_post(
        request: Request,
        name: str = Form(...),
        surname: str = Form(...),
        birthdate: str = Form(...),
        phone: str = Form(...),
        location: str = Form(...),
        image: UploadFile = File(None),
        favorite_tags: Optional[List[str]] = Form(None),
        db: Session = Depends(database.get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        # Валидация даты
        datetime.strptime(birthdate, "%Y-%m-%d")

        user = db.query(User).filter(User.id == current_user.id).first()

        # Обновляем только разрешённые поля
        user.name = name
        user.surname = surname
        user.birthdate = birthdate
        user.phone = phone
        user.location = location

        # Обработка тегов
        db.query(UserCategory).filter(UserCategory.user_id == user.id).delete()

        if favorite_tags:
            for tag_name in favorite_tags:
                tag_name = tag_name.strip()
                if tag_name:
                    category = db.query(Category).filter(Category.name == tag_name).first()
                    if not category:
                        category = Category(name=tag_name)
                        db.add(category)
                        db.flush()
                    db.add(UserCategory(user_id=user.id, category_id=category.id))

        # Обработка изображения (без await)
        if image and image.filename:
            user.avatar_url = save_uploaded_file(image)  # Убрали await
        elif not user.avatar_url:
            user.avatar_url = "/static/default-avatar.jpg"

        db.commit()
        return RedirectResponse("/profile", status_code=303)

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Неверный формат даты: {str(e)}")

# @router.get("/user-registrations", response_model=list[schemas.RegistrationResponse])
# def get_user_registrations(user_id: int, db: Session = Depends(database.get_db)):
#     return crud.get_user_registrations(db, user_id)

