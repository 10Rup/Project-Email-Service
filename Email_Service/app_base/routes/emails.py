from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..database import SessionLocal
from ..models import Email, Attachment
from ..schemas import EmailCreate, EmailReply
from ..auth import get_current_user



router= APIRouter()



def get_db():

    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

# Get Email Routes
@router.get('/inbox')
def get_inbox(page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    offset = (page - 1) * limit
    emails = db.query(Email).filter(Email.receiver == current_user.email, Email.is_deleted == False).order_by(Email.created_at.desc(), Email.id.desc()).offset(offset).limit(limit).all()
    
    return emails


@router.get('/sent')
def get_sent_emails(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    emails = db.query(Email).filter(Email.sender == current_user.email, Email.is_deleted == False).order_by(Email.created_at.desc(), Email.id).all()

    return emails

@router.get('/thread/{thread_id}')
def get_thread(thread_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    emails = db.query(Email).filter(Email.thread_id == thread_id, Email.is_deleted == False).order_by(Email.created_at).all()

    return emails


@router.get("/search")
def search_emails(q: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    emails = db.query(Email).filter(Email.is_deleted == False,
                                    or_(
                                        Email.subject.ilike(f"%{q}%"),
                                        Email.body.ilike(f"%{q}%"),
                                        Email.sender.ilike(f"%{q}%")
                                    ),
                                    
                                    or_(
                                        Email.receiver == current_user.email,Email.sender == current_user.email
                                    )).order_by(Email.created_at.desc()).all()

    return emails


@router.get("/attachments/{email_id}")
def get_attachment(email_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    attachments = db.query(Attachment).filter(Attachment.email_id == email_id).all()

    return attachments


@router.get("/download/{attachment_id}")
def get_attachment(attachment_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()

    return FileResponse(attachment.file_path)


# Post Email Routes

# @router.post('/send')
# def send_email(email: EmailCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

#     new_email = Email(
#         thread_id = None,
#         sender=current_user.email,
#         receiver=email.receiver,
#         subject=email.subject,
#         body=email.body,
#         created_at=datetime.now(timezone.utc)
#     )
#     db.add(new_email)
#     db.commit()
#     db.refresh(new_email)

#     #set thread id
#     new_email.thread_id = new_email.id
#     db.commit()

#     return {'message':'Email sent'}

@router.post("/send")
def send_email(receiver: str = Form(...), subject: str = Form(...), body: str =  Form(...), file: UploadFile = File(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    new_email = Email(
        thread_id = None,
        sender = current_user.email,
        receiver = receiver,
        subject = subject,
        body = body
    )


    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    new_email.thread_id = new_email.id
    db.commit()

    if file:

        file_location = f'uploads/{datetime.now(timezone.utc).timestamp()}{file.filename}'

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        attachment = Attachment(
            email_id = new_email.id,
            file_path = file_location
        )

        db.add(attachment)
        db.commit()
    
    return {'message': 'Email Sent'}




@router.post("/reply")
def reply_email(reply: EmailReply, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    new_email = Email(
        thread_id = reply.thread_id,
        sender = current_user.email,
        receiver = reply.receiver,
        subject = reply.subject,
        body = reply.body
    )

    db.add(new_email)
    db.commit()

    return {'message': "reply sent"}



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



# emails drafts

@router.post("/draft")
def save_draft(receiver: str = Form(None), subject: str = Form(None), body: str = Form(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    new_draft = Email(
        thread_id = None,
        sender = current_user.email,
        receiver = receiver,
        subject = subject,
        body = body,
        status = "draft"
    )

    db.add(new_draft)
    db.commit()
    db.refresh(new_draft)
    new_draft.thread_id  = new_draft.id
    db.commit()
    return {'message': "Draft saved"}

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