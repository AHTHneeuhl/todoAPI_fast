from fastapi import APIRouter, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from models import User
from db import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

bcrypt_ctx = CryptContext(schemes=["bcrypt"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_ctx.verify(password, user.hashed_password):
        return False
    return True


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    user = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_ctx.hash(user_request.password),
        is_active=True,
    )
    db.add(user)
    db.commit()


@router.post("/token")
async def access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Failed Authentication"
    return "Successful Authentication"
