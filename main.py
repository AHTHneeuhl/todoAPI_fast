from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
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


@app.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todo).all()


@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="todo not found")
