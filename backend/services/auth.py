import secrets
from sqlalchemy.orm import Session
from backend import crud

def generate_verification_code(db: Session, email: str):
    code = str(secrets.randbelow(900000) + 100000)  # 6-значный код
    crud.save_verification_code(db, email, code)
    return code

def validate_verification_code(db: Session, email: str, code: str):
    db_code = crud.get_verification_code(db, email)
    return db_code and db_code.code == code
