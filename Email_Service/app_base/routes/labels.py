from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Email, Label, EmailLabel
from ..auth import get_current_user


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create")
def create_label(name: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    new_label = Label(name=name)
    db.add(new_label)
    db.commit()
    db.refresh(new_label)

    return {'message': f'new label {name} created'}



@router.post('/assign')
def assign_email(email_id: int, label_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    new_email_label = EmailLabel(email_id=email_id, label_id=label_id)

    db.add(new_email_label)
    db.commit()
    
    return {'message': 'label Assigned'}


@router.get('/{label_id}')
def get_email_by_label(label_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    emails = db.query(Email).join(EmailLabel, EmailLabel.email_id==Email.id).filter(EmailLabel.label_id==label_id).all()

    return emails