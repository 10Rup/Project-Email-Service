from sqlalchemy.orm import Session
from ..models import Email, Attachment
from datetime import datetime, timezone
import shutil
import os

def send_email(db: Session, sender, receiver, subject, body, file):

    new_email = Email(
        sender = sender, 
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
    return new_email


def reply_email(db: Session, thread_id, sender, receiver, body):
    
    re_email = Email(
        thread_id = thread_id,
        sender = sender,
        receiver = receiver,
        subject = "Re:",
        body = body

    )
    db.add(re_email)
    db.commit()

    return re_email



def save_draft(receiver: str, subject: str, body: str, db: Session, sender: str):
    new_draft = Email(
        thread_id = None,
        sender = sender,
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