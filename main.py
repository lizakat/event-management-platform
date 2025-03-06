import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from backend.database import engine
from backend.models import Base
from backend.routes import auth, users, events, pages
from backend.templates import FRONTEND_DIR
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
app.mount("/public", StaticFiles(directory=os.path.join(FRONTEND_DIR, "public")), name="public")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(pages.router, prefix="", tags=["Pages"])

