import os
from pathlib import Path
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))
