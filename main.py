from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from models import Todo, Base
from db import engine, SessionLocal

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todo).all()
