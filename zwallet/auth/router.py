import base64
import os
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

from zwallet.dependencies import Session, Settings, Tokens

from .models import User


class UserRequest(BaseModel):
    username: str
    password: str


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _authenticated_user(
    session: Session, username: str, password: str
) -> Optional[User]:
    user = session.query(User).filter_by(username=username).first()

    if not user:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user


@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(request: UserRequest, session: Session):
    if session.query(User).filter_by(username=request.username).filter_by().first():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User {request.username} already exists",
        )
    hashed_password = pwd_context.hash(request.password)
    salt = base64.urlsafe_b64encode(os.urandom(16))
    user = User(username=request.username, password=hashed_password, salt=salt)
    session.add(user)
    session.commit()
    return user


@router.post("/token")
async def login_for_access_token(
    session: Session,
    settings: Settings,
    tokens: Tokens,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = _authenticated_user(session, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.auth_exp)

    access_token = tokens.create_access_token(
        username=user.username,
        password=form_data.password,
        salt=user.salt,
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
