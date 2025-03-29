import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    # Usa banco de dados em memória para isolamento dos testes
    engine = create_engine('sqlite:///:memory:')

    # Cria todas as tabelas
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session  # Retorna a sessão criada, quando o argumento session for passado para a função o que vai ser retornado é o que está acompanhado do "yield" e a fixture vai parar ali, depois que o teste terminar a sessão será fechada e o banco de dados em memória será destruído

    # Limpa todas as tabelas, SÓ É EXECUTADO AO FINAL DO TESTE
    table_registry.metadata.drop_all(engine)
