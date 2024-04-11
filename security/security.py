from datetime import datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import config as config
from db.crud import UserRepository
from db.models import User
from db.schemas import UserAuth
from security.pwdcrypt import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await UserRepository.get_user(session, username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User):
    to_encode = {"id": user.id, "sub": user.username, "position": user.position}
    expire = datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


# Функция получения User'а по токену
def get_user_from_token(token: str = Depends(oauth2_scheme)) -> UserAuth:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return UserAuth(
            id=payload.get("id"),
            username=payload.get("sub"),
            position=payload.get("position"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
