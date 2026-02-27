import jwt
from typing import Dict, Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

from car_api.core.database import get_session
from car_api.core.settings import Settings
from car_api.models import User

pwd_context = PasswordHash.recommended()
settings = Settings()
secutiry_http_bearer = HTTPBearer()


def get_password_hash(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({ "exp": expire })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Dict:
    try:

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token expirado",
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )
    
    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token inválido",
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession
) -> Optional[User] | None:
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(secutiry_http_bearer),
    db: AsyncSession = Depends(get_session)
) -> User:
    
    payload = verify_token(credentials.credentials)

    user_id_str = payload.get("sub")

    if not user_id_str:

        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais inválidas",
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    try:
        user_id = int(user_id_str)

    except (ValueError, TypeError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciais inválidas",
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Usuário não encontrado",
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )
    
    return user


    