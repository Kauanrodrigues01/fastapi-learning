from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import FilterTodo, TodoPublicSchema, TodoSchema, TodoUpdateSchema
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterTodo = Annotated[FilterTodo, Query()]


@router.post('', response_model=TodoPublicSchema, status_code=HTTPStatus.CREATED)
def create_todo(todo: TodoSchema, user: T_CurrentUser, session: T_Session):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('', response_model=list[TodoPublicSchema])
def list_todos(session: T_Session, user: T_CurrentUser, filter_todo: T_FilterTodo):
    query = select(Todo).where(Todo.user_id == user.id)

    if filter_todo.title:
        query = query.filter(Todo.title.contains(filter_todo.title))

    if filter_todo.description:
        query = query.filter(Todo.description.contains(filter_todo.description))

    if filter_todo.state:
        query = query.filter(Todo.state == filter_todo.state)

    todos = session.scalars(query.offset(filter_todo.skip).limit(filter_todo.limit)).all()

    return todos


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_todo(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = session.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id))

    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    session.delete(todo)
    session.commit()


@router.patch('/{todo_id}', response_model=TodoPublicSchema)
def patch_todo(todo_id: int, todo: TodoUpdateSchema, session: T_Session, user: T_CurrentUser):
    db_todo = session.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id))

    if not db_todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')

    # "exclude_unset=True", faz com que o dicionario retornado já exclua os campos com o valor igual a None
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
