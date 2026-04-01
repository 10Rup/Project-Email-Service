from fastapi import APIRouter, Depends, UploadFile, File, Form, Request # type: ignore
from fastapi.responses import FileResponse, RedirectResponse # type: ignore
import shutil
import os
from sqlalchemy import or_ # type: ignore
from sqlalchemy.orm import Session # type: ignore
from ..database import SessionLocal
from ..models import Email, Attachment
from ..schemas import EmailReply
from ..auth import get_current_user
from ..services import email_service

router= APIRouter()

def get_db():

    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

# send email
@router.post("/send")
def send_email(request: Request, receiver: str = Form(...), subject: str = Form(...), body: str = Form(...), file: UploadFile = File(None), db: Session = Depends(get_db)):
    
    email = email_service.send_email(db, sender=request.session.get('user'), 
    receiver=receiver, subject=subject, body=body, file=file)
    
    return RedirectResponse(url='/inbox', status_code=303)

# Update Email status
@router.put("/read/{email_id}")
def mark_as_read(email_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    email = db.query(Email).filter(Email.id == email_id, Email.receiver == current_user.email).first()
    if not email:
        return {'message': 'Email not found'}
    email.is_read = True
    db.commit()
    return {'message': 'Email marked as read'}

# Delete Email
@router.delete('/delete/{email_id}')
def delete_email(email_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        return {'message':'Email not found'}
    if email.receiver != current_user.email and email.sender != current_user.email:
        return {'message': 'Not Authorized'}
    email.is_deleted = True
    db.commit()
    return {'message':'Email deleted'}

@router.post("/reply")
def reply_email(request: Request, thread_id: int = Form(...), receiver: str = Form(...), body: str = Form(...), db: Session = Depends(get_db)):
    
    re_email = email_service.reply_email(db, thread_id, sender = request.session.get('user'), receiver=receiver, body=body)
    return RedirectResponse(url=f'/thread/{thread_id}', status_code=303)

# emails drafts
@router.post("/draft")
def save_draft(receiver: str = Form(None), subject: str = Form(None), body: str = Form(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_draft = email_service.save_draft(receiver, subject, body, db, current_user.email)
    return new_draft

@router.get("/drafts")
def get_drafts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    drafts = db.query(Email).filter(Email.sender == current_user.email, Email.status == "draft", Email.is_deleted == False).all()
    return drafts

@router.put("/draft/{draft_id}")
def send_draft(draft_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    draft = db.query(Email).filter(Email.id == draft_id, Email.sender == current_user.email, Email.status == "draft").first()
    if not draft:
        return {'message': 'Draft not Found'}
    draft.status = 'sent'
    db.commit()
    return {'message': 'Draft sent'}


@router.get('/inbox')
def get_inbox(page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    offset = (page - 1) * limit
    emails = db.query(Email).filter(Email.receiver == current_user.email, Email.is_deleted == False).order_by(Email.created_at.desc(), Email.id.desc()).offset(offset).limit(limit).all()
    return emails

@router.get('/sent')
def get_sent_emails(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emails = db.query(Email).filter(Email.sender == current_user.email, Email.is_deleted == False).order_by(Email.created_at.desc(), Email.id).all()
    return emails

# @router.get('/thread/{thread_id}')
# def get_thread(request: Request, thread_id: int, db: Session = Depends(get_db)):

#     user = request.session.get('user')
    
#     if not user:
#         return RedirectResponse(url='/login')
    
#     emails = db.query(Email).filter(Email.thread_id == thread_id, Email.is_deleted == False).order_by(Email.created_at).all()

    

#     return emails

@router.get("/search")
def search_emails(q: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emails = db.query(Email).filter(Email.is_deleted == False,or_(Email.subject.ilike(f"%{q}%"),Email.body.ilike(f"%{q}%"),Email.sender.ilike(f"%{q}%")),or_(Email.receiver == current_user.email,Email.sender == current_user.email)).order_by(Email.created_at.desc()).all()
    return emails

@router.get("/attachments/{email_id}")
def get_attachment(email_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    attachments = db.query(Attachment).filter(Attachment.email_id == email_id).all()
    return attachments

@router.get("/download/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    return FileResponse(attachment.file_path)
