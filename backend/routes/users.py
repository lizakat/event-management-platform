from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import database, schemas, crud

router = APIRouter()

@router.get("/profile/{user_id}", response_model=schemas.UserResponse)
def get_profile(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/edit-profile/{user_id}", response_model=schemas.UserResponse)
def edit_profile(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return crud.update_user(db=db, db_user=db_user, user_update=user_update)


# @router.get("/user-registrations", response_model=list[schemas.RegistrationResponse])
# def get_user_registrations(user_id: int, db: Session = Depends(database.get_db)):
#     return crud.get_user_registrations(db, user_id)

#
# @router.post("/create-user")
# def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
#     return crud.create_user(db=db, user=user)