from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query, responses
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import FilterPage, UserPublicSchema, UserSchema
from fast_zero.security import get_current_user, get_password_hash
from fast_zero.utils import get_object_or_404, validate_username_or_email

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[FilterPage, Query()]  # A junção do modelo "FilterPage" com o objeto "Query()" do FastAPI, faz com que os atributos do modelo "FilterPage" virem QueryParams do endpoint


@router.post(
    '',
    status_code=HTTPStatus.CREATED,
    response_class=responses.JSONResponse,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema, session: T_Session):
    """Cria um novo usuário e retorna o usuário criado."""
    validate_username_or_email(username=user.username, email=user.email, session=session)

    db_user = User(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user  # Retorna o usuário criado


@router.get('', status_code=HTTPStatus.OK, response_model=list[UserPublicSchema])
def list_users(session: T_Session, filter_page: T_FilterPage):
    """Retorna uma lista de usuários com paginação."""
    users = session.scalars(select(User).offset(filter_page.skip).limit(filter_page.limit)).all()
    return users


@router.put('', response_model=UserPublicSchema)
def update_user(user: UserSchema, session: T_Session, current_user: T_CurrentUser):
    """Atualiza um usuário existente"""
    validate_username_or_email(
        username=user.username,
        email=user.email,
        session=session,
        user_id=current_user.id,  # Para excluir o usuário que está sendo atualizado na hora de verificar se já tem um usuário registrado com o esse username ou email.
    )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('', status_code=HTTPStatus.NO_CONTENT)
def delete_user(session: T_Session, current_user: T_CurrentUser):
    """Deleta um usuário existente"""
    session.delete(current_user)
    session.commit()


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def detail_user(user_id: int, session: T_Session):
    """Retorna os detalhes de um usuário específico."""
    db_user = get_object_or_404(model=User, obj_id=user_id, session=session, detail='User not found')

    return db_user
