from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException, responses
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    UserPublicSchema,
    UserSchema,
)
from fast_zero.utils import get_object_or_404, validate_username_or_email

app = FastAPI(
    debug=True,
    title='Aula Sobre Banco de Dados',
    description='Configurando Banco de Dados e Gerenciando Migrações com SQLalchemy e Alembic',
    version='0.1.0',
)


@app.post(
    '/users',
    status_code=HTTPStatus.CREATED,
    response_class=responses.JSONResponse,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema, session=Depends(get_session)):
    """Cria um novo usuário e retorna o usuário criado."""
    validate_username_or_email(
        username=user.username, 
        email=user.email, 
        session=session
    )

    db_user = User(
        **user.model_dump()
    )  # Cria um novo usuário com os dados recebidos
    session.add(db_user)  # Adiciona o usuário na sessão
    session.commit()  # Salva as alterações no banco de dados
    session.refresh(
        db_user
    )  # Atualiza o objeto db_user com os dados do banco de dados (incluindo o ID gerado)

    return db_user  # Retorna o usuário criado


@app.get(
    '/users', status_code=HTTPStatus.OK, response_model=list[UserPublicSchema]
)
def read_users(skip: int = 0, limit: int = 100, session=Depends(get_session)):
    """Retorna uma lista de usuários com paginação."""
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return users


@app.put('/users/{user_id}', response_model=UserPublicSchema)
def update_user(user_id: int, user: UserSchema, session=Depends(get_session)):
    """Atualiza um usuário existente"""
    db_user = get_object_or_404(
        model=User,
        obj_id=user_id,
        session=session,
        detail='User not found'
    )

    validate_username_or_email(
        username=user.username,
        email=user.email,
        session=session,
        user_id=db_user.id  # Para excluir o usuário que está sendo atualizado na hora de verificar se já tem um usuário registrado com o esse username ou email.
    )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, session=Depends(get_session)):
    """Deleta um usuário existente"""
    db_user = get_object_or_404(
        model=User,
        obj_id=user_id,
        session=session,
        detail='User not found'
    )

    session.delete(db_user)
    session.commit()


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def detail_user(user_id: int, session=Depends(get_session)):
    """Retorna os detalhes de um usuário específico."""
    db_user = get_object_or_404(
        model=User,
        obj_id=user_id,
        session=session,
        detail='User not found'
    )

    return db_user
