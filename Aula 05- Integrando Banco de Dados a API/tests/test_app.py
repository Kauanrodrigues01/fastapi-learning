from http import HTTPStatus

from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas import UserPublicSchema


def test_create_user_success(client, session):
    user_data = {
        'username': 'test_name',
        'email': 'teste@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    response_user_data = user_data.copy()
    del response_user_data['password']
    response_user_data['id'] = 1

    # Verifica se a response do endpoint é no modelo UserPublicSchema
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == response_user_data

    # Verifica se o usuário foi realmente criado no banco de dados
    db_user = session.scalar(
        select(User).where(
            (User.id == 1)
            & (User.username == user_data['username'])
            & (User.email == user_data['email'])
        )
    )

    assert db_user is not None


def test_create_user_with_duplicate_username(client, user):
    user_data = {
        'username': user.username,  # mesmo username
        'email': 'teste@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already registered'}


def test_create_user_with_duplicate_email(client, user):
    user_data = {
        'username': 'teste username', 
        'email': user.email,  # mesmo email
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already registered'}


def test_read_users_success(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_read_users_with_user_success(client, user):
    """
    - a função "model_validade" recebe um dict e retorna um objeto do tipo UserPublicSchema já validado com os dados da variável user

    - "user.__dict__" retorna um dicionário com os atributos do objeto user

    - a função "model_dump" transforma o objeto UserPublicSchema em um dicionário
    """
    response = client.get('/users')

    user_schema = UserPublicSchema.model_validate(user.__dict__)
    user_data = (
        user_schema.model_dump()
    )  # Transforma o objeto em um dicionário

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [user_data]


def test_update_user_success(client, user, session):
    user_data = {
        'username': 'test_updated_name',
        'email': 'teste_updated@example.com',
        'password': 'test_updated_secret',
    }

    response = client.put('/users/1', json=user_data)

    response_user_data = user_data.copy()
    del response_user_data['password']
    response_user_data['id'] = 1

    assert response.status_code == HTTPStatus.OK
    assert response.json() == response_user_data

    session.refresh(
        user
    )  # Atualiza o objeto user com os dados do banco de dados
    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.password == user_data['password']


def test_updated_user_not_found(client):
    user_data = {
        'username': 'test_updated_name',
        'email': 'teste_updated@example.com',
        'password': 'updated_secret',
    }

    response = client.put('/users/10000', json=user_data)  # ID inexistente

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_with_duplicate_username(client, user, session):
    # Criando um segundo usuário
    user2 = User(
        username='user2',
        email='user2@example.com',
        password='user2password'
    )
    session.add(user2)
    session.commit()
    session.refresh(user2)

    user2_update_data = {
        'username': user.username,  # mesmo username
        'email': 'teste_updated@example.com',
        'password': 'test_updated_secret',
    }

    # Tentando atualizar o username do user2 para o mesmo do user
    response = client.put('/users/2', json=user2_update_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already registered'}


def test_update_user_with_duplicate_email(client, user, session):
    # Criando um segundo usuário
    user2 = User(
        username='user2',
        email='user2@example.com',
        password='user2password'
    )
    session.add(user2)
    session.commit()
    session.refresh(user2)

    user2_update_data = {
        'username': 'test_updated_name',
        'email': user.email,  # mesmo email
        'password': 'test_updated_secret',
    }

    # Tentando atualizar o email do user2 para o mesmo do user
    response = client.put('/users/2', json=user2_update_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already registered'}


def test_delete_user_success(client, user, session):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text

    # Verifica se o usuário foi realmente deletado do banco de dados
    db_user = session.scalar(select(User).where(User.id == 1))
    assert db_user is None


def test_delete_user_not_found(client):
    response = client.delete('/users/10000')  # ID inexistente

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_detail_user(client, user):
    response = client.get('/users/1')

    user_schema = UserPublicSchema.model_validate(user.__dict__)
    user_data = user_schema.model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_data


def test_detail_user_not_found(client):
    response = client.get('/users/10000')  # ID inexistente
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
