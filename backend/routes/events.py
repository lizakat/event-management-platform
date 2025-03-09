from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import database, schemas, crud

router = APIRouter()


# @router.post("/create-event", response_model=schemas.EventResponse)
# def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
#     return crud.create_event(db=db, event=event)
#
#
# @router.put("/edit-event/{event_id}", response_model=schemas.EventResponse)
# def edit_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(database.get_db)):
#     db_event = crud.get_event_by_id(db, event_id)
#     if not db_event:
#         raise HTTPException(status_code=404, detail="Событие не найдено")
#
#     return crud.update_event(db=db, db_event=db_event, event=event)
#
#
# @router.delete("/delete-event/{event_id}")
# def delete_event(event_id: int, db: Session = Depends(database.get_db)):
#     if not crud.delete_event(db, event_id):
#         raise HTTPException(status_code=404, detail="Событие не найдено")
#
#     return {"message": "Событие удалено"}
#
#
# @router.get("/favourite-events", response_model=list[schemas.FavouriteEventResponse])
# def get_favourite_events(user_id: int, db: Session = Depends(database.get_db)):
#     return crud.get_favourite_events(db, user_id)
