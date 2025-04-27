from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import User


def get_object_or_404(model, obj_id: int, session: Session, detail: str = 'Object not found'):
    """Função para obter um objeto ou lançar uma exceção 404."""
    obj = session.scalar(select(model).where(model.id == obj_id))

    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)

    return obj


def validate_username_or_email(username: str, email: str, session: Session, user_id: int = None):
    """Verifica se o username ou email já estão cadastrados."""
    db_user = session.scalar(select(User).where((User.username == username) | (User.email == email)))

    if db_user and db_user.id != user_id:
        if db_user.username == username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already registered',
            )
        elif db_user.email == email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already registered',
            )
