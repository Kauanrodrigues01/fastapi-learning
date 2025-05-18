from fast_zero.models import Todo, TodoState, User


def test_create_model_user(session):
    user = User(username='test', email='test@test.com', password='secret')
    session.add(user)  # Adiciona o usuário na sessão, para depois ser salvo
    session.commit()

    # IMPORTANTE: Refresca a sessão para limpar o cache
    session.refresh(user)

    # As asserções dentro da sessão
    assert user.username == 'test'
    assert user.password == 'secret'
    assert user.id is not None  # Verifica se o ID foi gerado
    assert user.created_at is not None  # Verifica o timestamp
    assert user.id == 1

    # Teste opcional: Verifica se o usuário realmente foi persistido
    session.expire_all()  # Limpa o cache
    db_user = session.get(User, user.id)  # Busca o usuário pelo ID
    assert db_user.id == 1
    assert db_user.username == 'test'


def test_create_model_todo(session, user):
    todo = Todo(title='test', description='testtest', state=TodoState.draft, user_id=user.id)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    session.expire_all()

    db_todo = session.get(Todo, todo.id)

    assert db_todo.title == 'test'
    assert db_todo.description == 'testtest'
    assert db_todo.state == TodoState.draft
    assert db_todo.user_id == user.id
    assert db_todo.created_at is not None
    assert db_todo.updated_at is not None
