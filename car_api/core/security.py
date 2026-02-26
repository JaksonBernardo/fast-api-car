import jwt

from fastapi import HTTPException, status
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

from car_api.core.settings import Settings


pwd_context = PasswordHash.recommended()
settings = Settings()

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
