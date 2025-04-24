from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException, responses
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import TokenSchema, UserPublicSchema, UserSchema
from fast_zero.security import create_access_token, get_current_user, get_password_hash, verify_password
from fast_zero.utils import get_object_or_404, validate_username_or_email

app = FastAPI(
    debug=True,
    title='Aula Sobre Banco de Dados',
    description='Configurando Banco de Dados e Gerenciando Migrações com SQLalchemy e Alembic',
    version='0.1.0',
)


@app.post('/token', response_model=TokenSchema)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(
        select(User).where(
            (User.username == form_data.username) | (User.email == form_data.username)
        )
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data_payload={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@app.post(
    '/users',
    status_code=HTTPStatus.CREATED,
    response_class=responses.JSONResponse,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    """Cria um novo usuário e retorna o usuário criado."""
    validate_username_or_email(
        username=user.username, email=user.email, session=session
    )

    db_user = User(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(
        db_user
    )

    return db_user  # Retorna o usuário criado


@app.get(
    '/users', status_code=HTTPStatus.OK, response_model=list[UserPublicSchema]
)
def read_users(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_session),
):
    """Retorna uma lista de usuários com paginação."""
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return users


@app.put('/users', response_model=UserPublicSchema)
def update_user(
    user: UserSchema,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user)
):
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


@app.delete('/users', status_code=HTTPStatus.NO_CONTENT)
def delete_user(session=Depends(get_session), current_user: User = Depends(get_current_user)):
    """Deleta um usuário existente"""
    session.delete(current_user)
    session.commit()


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def detail_user(user_id: int, session=Depends(get_session)):
    """Retorna os detalhes de um usuário específico."""
    db_user = get_object_or_404(
        model=User, obj_id=user_id, session=session, detail='User not found'
    )

    return db_user
