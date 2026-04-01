from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import User
from ..auth import create_access_token, decode


def create_user(db: Session, email: str, password: str):

    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="User Already Registered")

    new_user = User(
        email = email,
        password = password

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def user_login(db: Session, email: str, password: str):
    
    user = db.query(User).filter(User.email == email, User.password == password).first()

    if not user:
        raise HTTPException(status_code=400, detail="invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


