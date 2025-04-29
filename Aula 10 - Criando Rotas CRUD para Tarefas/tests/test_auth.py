from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time

from fast_zero.settings import settings


def test_get_token(client, user):
    response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_with_invalid_password(client, user):
    response = client.post('/auth/token', data={'username': user.email, 'password': 'invalid_password'})
    json_response = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert json_response['detail'] == 'Incorrect email or password'


def test_get_token_with_invalid_email(client, user):
    response = client.post('/auth/token', data={'username': 'invalid_email@example.com', 'password': user.clean_password})
    json_response = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert json_response['detail'] == 'Incorrect email or password'


def test_token_expired_after_time(client, user):
    now = datetime(2025, 4, 27, 12, 0, 0)

    # congela o tempo no momento de criação do token
    with freeze_time(now):
        response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
        token = response.json()['access_token']

    token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # Avança o tempo para após a expiração do token
    expired_time = now + timedelta(minutes=token_expire_minutes + 1)

    with freeze_time(expired_time):
        response = client.put(
            '/users',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, user, create_token):
    token = create_token(user.email)
    response = client.post('/auth/refresh-token', headers={'Authorization': f'Bearer {token}'})

    json_response = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in json_response
    assert 'token_type' in json_response
    assert json_response['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client, user):
    now = datetime(2025, 4, 27, 12, 0, 0)

    with freeze_time(now):
        response = client.post('/auth/token', data={'username': user.email, 'password': user.clean_password})
        token = response.json()['access_token']

    token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expired_time = now + timedelta(minutes=token_expire_minutes + 1)

    with freeze_time(expired_time):
        response = client.post(
            '/auth/refresh-token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
