from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services import label_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create")
def create_label(name: str, db: Session = Depends(get_db)):
    new_label = label_service.create_label(db, name)
    return new_label

@router.post('/assign')
def assign_emaillabel(email_id: int, label_id: int, db: Session = Depends(get_db)):
    assign_label = label_service.assign_email_label(db,email_id, label_id)
    return assign_label  
    

@router.get('/{label_id}')
def get_email_by_label(label_id: int, db: Session = Depends(get_db)):
    emails = label_service.get_labeled_emails(db, label_id)
    return emails