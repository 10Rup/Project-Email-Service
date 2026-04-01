from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..database import SessionLocal
from ..models import User
from ..schemas import UserCreate, UserLogin, Token
from ..auth import create_access_token, decode    

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()



@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}




@router.post("/login",  response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    
    db_user = db.query(User).filter(User.email == user.email, User.password == user.password).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="invalid credentials")
    
    access_token = create_access_token(
        data={'sub': db_user.email}
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.post('/authtest')
def auth_test(decoded: str = Depends(decode)):
    return decoded