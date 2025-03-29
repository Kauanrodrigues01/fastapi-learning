from http import HTTPStatus

from fastapi import FastAPI, HTTPException, responses

from fast_zero.schemas import (
    Message,
    UserDBSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)

app = FastAPI(
    debug=True,
    title='Aulas do Dunossauro',
    description='Aulas',
    version='0.1.0',
)

database = []  # Banco de dados Falso


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=Message,
    response_description='Retorna uma mensagem Hello world para o usuário',
)
def hello_world():
    return {'message': 'Hello world'}


@app.post(
    '/users',
    status_code=HTTPStatus.CREATED,
    response_class=responses.JSONResponse,
    response_model=UserPublicSchema,
)
def create_user(user: UserSchema):
    """
    - O parâmetro "response_model=UserPublicSchema" já retira o campo "password" e qualquer outro campo que não esteja no Schema "UserPublicSchema" dá resposta
    """
    user_with_id = UserDBSchema(id=len(database) + 1, **user.model_dump())
    database.append(user_with_id)
    return user_with_id


@app.get('/users', status_code=HTTPStatus.OK, response_model=UserListSchema)
def read_users():
    return {'users': database}


@app.put('/users/{user_id}', response_model=UserPublicSchema)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDBSchema(id=user_id, **user.model_dump())
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    for index, user in enumerate(database):
        if user.id == user_id:
            del database[index]
            return
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='User not found'
    )


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublicSchema,
)
def detail_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user = database[user_id - 1]

    return user
