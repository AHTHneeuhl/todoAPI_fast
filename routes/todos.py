from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from models import Todo
from db import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get("/auth")
async def get_user():
    return {"user": "authenticated"}


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todo).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="todo not found")


@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo = Todo(**todo_request.model_dump())
    db.add(todo)
    db.commit()


@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        todo.title = todo_request.title
        todo.description = todo_request.description
        todo.priority = todo_request.priority
        todo.completed = todo_request.completed

        db.add(todo)
        db.commit()

    else:
        raise HTTPException(status_code=404, detail="todo not found")


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is not None:
        db.delete(todo)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="todo not found")
