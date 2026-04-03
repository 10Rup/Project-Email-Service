from fastapi import FastAPI, Request  # type: ignore
from .database import engine
from .models import Base
from .routes import users, emails, labels, pages
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(root_path="/email")

app.add_middleware(SessionMiddleware, secret_key="SUPER_SECRET_KEY")

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="app/templates")



app.include_router(pages.router)
app.include_router(users.router, prefix='/users', tags=["Users"])
app.include_router(emails.router, prefix='/emails', tags=['Emails'])
app.include_router(labels.router, prefix='/labels', tags=['Labels'])

@app.get("/")
def home():
    return {'message':"email server is running"}
