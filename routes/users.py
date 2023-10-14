from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from models import User
from db import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authorization failed")
    return db.query(User).filter(User.id == user.get("id")).first()


@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    user: user_dependency, db: db_dependency, user_request: UserRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authorization failed")
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if not bcrypt_ctx.verify(user_request.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model.hashed_password = bcrypt_ctx.hash(user_request.new_password)
    db.add(user_model)
    db.commit()
