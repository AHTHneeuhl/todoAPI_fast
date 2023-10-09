from fastapi import FastAPI
from models import Base
from db import engine
from routes import auth, todos

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
