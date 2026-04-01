from fastapi import APIRouter, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Email

router = APIRouter()
templates = Jinja2Templates("app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {'request': request}
    )

@router.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {'request': request}
    )


@router.get('/inbox')
def inbox_page(request: Request, db: Session = Depends(get_db)):
    user = request.session.get('user')
    emails = db.query(Email).filter(Email.receiver == user, Email.is_deleted == False).order_by(Email.created_at.desc()).all()
    
    return templates.TemplateResponse(
        'inbox.html',
        {
            'request': request,
            'emails': emails
        }
    )


@router.get('/compose')
def compose_page(request: Request):

    return templates.TemplateResponse(
        'compose.html',
        {
            'request': request
        }
    )



@router.get('/thread/{thread_id}')
def get_thread(request: Request, thread_id: int, db: Session = Depends(get_db)):

    user = request.session.get('user')
    
    if not user:
        return RedirectResponse(url='/login')
    
    emails = db.query(Email).filter(Email.thread_id == thread_id, Email.is_deleted == False).order_by(Email.created_at).all()

    

    return templates.TemplateResponse(
        'thread.html',
        {
            'request': request,
            'emails': emails,
            'thread_id': thread_id,
            'user': user
        }
    )


@router.get('/sent')
def sent_page(request: Request, db: Session = Depends(get_db)):

    user = request.session.get('user')

    if not user:
        return RedirectResponse("/login")
    
    sent_emails = db.query(Email).filter(
        Email.sender == user, 
        Email.is_deleted == False
    ).all()

    return templates.TemplateResponse(
        "sent.html",
        {
            'request': request, 'emails': sent_emails
        }
    )


@router.get('/logout')
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(url='/login')