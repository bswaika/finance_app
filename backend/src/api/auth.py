from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..models.user import User
from ..schemas.user import Token, UserCreate, UserRead
from ..services.auth_service import (
    authenticate_user,
    create_user,
    create_user_access_token,
    get_current_active_user,
)


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate) -> UserRead:
    user = create_user(user_in)
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
def login(data: LoginRequest) -> Token:
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_user_access_token(user)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_active_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
    )


