from fastapi import FastAPI
from .database import engine
from .models import Base

from .routes import users, emails, labels


app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(users.router, prefix='/users', tags=["Users"])
app.include_router(emails.router, prefix='/emails', tags=['Emails'])
app.include_router(labels.router, prefix='/labels', tags=['Labels'])


@app.get("/")
def home():
    return {'message':"email server is running"}

