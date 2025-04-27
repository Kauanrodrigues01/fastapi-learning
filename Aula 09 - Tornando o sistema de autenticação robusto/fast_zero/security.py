from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import settings

# Configuração inicial do sistema de autenticação
pwd_context = PasswordHash.recommended()
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/token')  # Define onde buscar o token (header Authorization)

# Configurações JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def get_password_hash(password: str):
    """Transforma a senha em um hash seguro para armazenamento"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Compara senha em texto plano com o hash armazenado"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data_payload: dict):
    """Gera um token JWT válido com os dados do usuário"""
    to_encode = data_payload.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode['exp'] = int(expire.timestamp())

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_schema),  # Obtém token automaticamente do header
):
    """
    Valida o token JWT e retorna o usuário correspondente.

    Fluxo:
    1. Extrai token do header Authorization (via oauth2_schema)
    2. Decodifica e verifica o token JWT
    3. Busca usuário no banco de dados
    4. Retorna objeto do usuário autenticado

    Se falhar em qualquer etapa, retorna erro 401 (Não autorizado)
    """
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        user_email = payload.get('sub')

        if not user_email:  # pragma: no cover
            credentials_exception

    except jwt.DecodeError:  # pragma: no cover
        raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == user_email))

    if not user:  # pragma: no cover
        credentials_exception

    return user
