from http import HTTPStatus


def test_hello_world_deve_retornar_ok(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello world'}


def test_create_user_success(client):
    user_data = {
        'username': 'test_name',
        'email': 'teste@example.com',
        'password': 'secret',
    }

    response = client.post('/users/', json=user_data)

    response_user_data = user_data.copy()
    del response_user_data['password']
    response_user_data['id'] = 1

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == response_user_data


def test_read_users_success(client):
    # O usuário que ira aparecer foi criado no teste anterior, só ira dar certo se todos os testes forem executados juntos
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'test_name',
                'email': 'teste@example.com',
            }
        ]
    }


def test_update_user_success(client):
    user_data = {
        'username': 'test_updated_name',
        'email': 'teste_updated@example.com',
        'password': 'updated_secret',
    }

    response = client.put('/users/1', json=user_data)

    response_user_data = user_data.copy()
    del response_user_data['password']
    response_user_data['id'] = 1

    assert response.status_code == HTTPStatus.OK
    assert response.json() == response_user_data


def test_updated_user_not_found(client):
    user_data = {
        'username': 'test_updated_name',
        'email': 'teste_updated@example.com',
        'password': 'updated_secret',
    }

    response = client.put('/users/10000', json=user_data)  # ID inexistente

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_success(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text

    response_get = client.get('/users')

    assert response_get.status_code == HTTPStatus.OK
    assert response_get.json() == {'users': []}


def test_delete_user_not_found(client):
    response = client.delete('/users/10000')  # ID inexistente

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_detail_user(client):
    # Criando um usuário novo, já que o outro foi deletado
    test_create_user_success(client)

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'test_name',
        'email': 'teste@example.com',
    }


def test_detail_user_not_found(client):
    response = client.get('/users/10000')  # ID inexistente
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
