import pytest
from factory.base import Factory
from factory.declarations import LazyAttribute, Sequence
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import create_access_token, get_password_hash


class UserFactory(Factory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'test{n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@gmail.com')
    password = LazyAttribute(lambda obj: f'{obj.username}@Password2463')


@pytest.fixture
def client(
    session,
):  # esse "session" chama a fixture session que está logo abaixo
    """
    Sobrescreve a dependência get_session para usar a sessão de teste, ou seja, quando ele for usar a session no endpoint ele vai usar a session que foi criada aqui e não a session padrão do banco de dados. Todo teste que chamar client vai usar essa session de teste.

    Utilizando isto, todos os endpoints que utilizam a dependência get_session (DB) durante os testes, vão usar a sessão de teste criada na fixture session. Isso garante que os testes não afetem o banco de dados real e que cada teste tenha um ambiente isolado.
    """

    def get_session_override():
        # Retorna uma sessão de banco de dados em memória para os testes
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    # Limpa a dependência sobrescrita após os testes
    app.dependency_overrides.clear()


@pytest.fixture
def session():
    # Usa banco de dados em memória para isolamento dos testes
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},  # Necessário para SQLite em threads diferentes
        poolclass=StaticPool,  # Usa um pool de conexão estático para evitar problemas de concorrência
    )

    # Cria todas as tabelas
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session  # Retorna a sessão criada, quando o argumento session for passado para a função o que vai ser retornado é o que está acompanhado do "yield" e a fixture vai parar ali, depois que o teste terminar a sessão será fechada e o banco de dados em memória será destruído

    # Limpa todas as tabelas, SÓ É EXECUTADO AO FINAL DO TESTE
    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session: Session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password  # Atribui dinamicamente um novo atributo a essa instância

    return user


@pytest.fixture
def user2(session: Session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password  # Atribui dinamicamente um novo atributo a essa instância

    return user


@pytest.fixture
def create_token():
    def _create_token(email: str):
        return create_access_token(data_payload={'sub': email})

    return _create_token
