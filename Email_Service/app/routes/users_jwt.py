from fastapi import APIRouter, Depends, Form # type: ignore
from sqlalchemy.orm import Session # type: ignore
from ..database import SessionLocal
from ..schemas import Token
from ..services import user_service


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()


@router.post("/register")
def register_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_user = user_service.create_user(db, email, password)
    return new_user


@router.post("/login",  response_model=Token)
def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_service.user_login(db, email, password)
    return user


# @router.post('/authtest')
# def auth_test(decoded: str = Depends(decode)):
#     return decoded