from http import HTTPStatus
from datetime import datetime

from factory.base import Factory
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice

from fast_zero.models import Todo, TodoState


class TodoFactory(Factory):
    class Meta:
        model = Todo

    title = Faker('text')
    description = Faker('text')
    state = FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, session, user, create_token):
    token = create_token(user.email)

    todo_data = {'title': 'test', 'description': 'testtest', 'state': TodoState.draft}

    response = client.post('/todos', headers={'Authorization': f'Bearer {token}'}, json=todo_data)

    todo_response_data = todo_data.copy()
    todo_response_data['id'] = 1

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == todo_response_data

    db_todo = session.get(Todo, 1)

    assert db_todo is not None


def test_create_todo_with_user_id(client, session, user, create_token):
    token = create_token(user.email)

    todo_data = {'title': 'test', 'description': 'testtest', 'state': TodoState.draft}

    client.post('/todos', headers={'Authorization': f'Bearer {token}'}, json=todo_data)

    db_todo = session.get(Todo, 1)

    assert db_todo.user_id == user.id


def test_list_todo(client, session, user, create_token):
    token = create_token(user.email)
    
    test_todo = TodoFactory(
        user_id=user.id,
        title="Tarefa importante",
        description="Descrição detalhada da tarefa",
        state=TodoState.doing
    )
    session.add(test_todo)
    session.commit()

    response = client.get(
        f'/todos',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    
    response_data = response.json()
    
    # Validação dos valores dos campos
    assert response_data[0]['id'] == test_todo.id
    assert response_data[0]['title'] == "Tarefa importante"
    assert response_data[0]['description'] == "Descrição detalhada da tarefa"
    assert response_data[0]['state'] == "doing"
    
    # Validação dos tipos dos campos
    assert isinstance(response_data[0]['id'], int)
    assert isinstance(response_data[0]['title'], str)
    assert isinstance(response_data[0]['description'], str)
    assert isinstance(response_data[0]['state'], str)



def test_list_todos_should_return_5_todos(client, session, user, create_token):
    token = create_token(user.email)

    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos',  # sem query
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


def test_list_todos_pagination_should_return_2_todos(client, session, user, create_token):
    token = create_token(user.email)

    limit_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        f'/todos?skip=1&limit={limit_todos}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == limit_todos


def test_list_todos_filter_title_should_return_5_todos(client, session, user, create_token):
    token = create_token(user.email)

    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1'))
    session.commit()

    response = client.get(
        '/todos?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(client, session, user, create_token):
    token = create_token(user.email)

    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, description='description'))
    session.commit()

    response = client.get(
        '/todos?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(client, session, user, create_token):
    token = create_token(user.email)

    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft))
    session.commit()

    response = client.get(
        '/todos?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(client, session, user, create_token):
    token = create_token(user.email)

    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()) == expected_todos


def test_delete_todo(client, session, user, create_token):
    token = create_token(user.email)

    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'})

    session.expire_all()
    db_todo = session.get(Todo, todo.id)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert db_todo is None


def test_delete_todo_with_nonexistent_id_should_return_not_found(client, user, create_token):
    # Testa quando tentamos deletar um TODO que não existe
    token = create_token(user.email)

    response = client.delete('/todos/10', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_delete_another_users_todo_should_return_not_found(client, session, user, user2, create_token):
    # Testa quando um usuário tenta deletar TODO de outro usuário
    token_user2 = create_token(user2.email)

    todo = TodoFactory(user_id=user.id)  # todo pertencente ao user
    session.add(todo)
    session.commit()

    response = client.delete(  # tentando deletar o todo pertencente ao user, mas estando logado com o user2
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token_user2}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo(client, session, user, create_token):
    token = create_token(user.email)

    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'

    session.expire_all()
    db_todo = session.get(Todo, todo.id)

    assert db_todo.title == 'teste!'


def test_patch_todo_error(client, user, create_token):
    token = create_token(user.email)

    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
