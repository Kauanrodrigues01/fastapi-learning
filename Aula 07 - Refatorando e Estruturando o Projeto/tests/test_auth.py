from http import HTTPStatus


def test_get_token(client, user):
    response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_with_invalid_password(client, user):
    response = client.post('/auth/token', data={'username': user.email, 'password': 'invalid_password'})
    json_response = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert json_response['detail'] == 'Incorrect email or password'


def test_get_token_with_invalid_email(client, user):
    response = client.post('/auth/token', data={'username': 'invalid_email@example.com', 'password': user.clean_password})
    json_response = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert json_response['detail'] == 'Incorrect email or password'
