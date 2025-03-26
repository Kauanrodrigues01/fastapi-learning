from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_hello_world_deve_retornar_ok():
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'Hello': 'World'}


def test_hello_name_deve_retornar_ok():
    response = client.get('/kauan')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'Hello': 'kauan'}
