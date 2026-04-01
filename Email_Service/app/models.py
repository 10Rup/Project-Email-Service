from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, index=True)
    sender = Column(String, index=True)
    receiver = Column(String, index=True)
    subject = Column(String, index=True)
    body = Column(String)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    status = Column(String, default='sent')
    created_at = Column(DateTime, default=datetime.now(timezone.utc))



class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))



class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)



class EmailLabel(Base):
    __tablename__ = "email_labels"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    label_id = Column(Integer, ForeignKey("labels.id"))