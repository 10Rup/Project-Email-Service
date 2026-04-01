from sqlalchemy.orm import Session
from ..models import Label, EmailLabel, Email


def create_label(db: Session, name: str):

    new_label = Label(
        name = name
    )
    db.add(new_label)
    db.commit()
    db.refresh(new_label)

    return new_label


def assign_email_label(db: Session, email_id: int, label_id: int):

    assign_label = EmailLabel(
        email = email_id,
        label_id = label_id
    )
    db.add(assign_label)
    db.commit()
    db.refresh(assign_label)

    return assign_label


def get_labeled_emails(db: Session, label_id: int):

    emails = db.query(Email).join(EmailLabel, EmailLabel.email_id==Email.id).filter(EmailLabel.label_id==label_id).all()

    return emails