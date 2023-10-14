from fastapi import APIRouter
from pydantic import BaseModel
from passlib.context import CryptContext
from models import User

router = APIRouter()

bcrypt_ctx = CryptContext(schemes=["bcrypt"])


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth")
async def create_user(user_request: UserRequest):
    user_model = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_ctx.hash(user_request.password),
        is_active=True,
    )

    return user_model
