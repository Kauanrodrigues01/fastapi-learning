from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

# Cria um registro para armazenar as classes de modelo (tabelas)
table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


# Decorador que converte a classe em um dataclass enquanto a registra como modelo SQLAlchemy
@table_registry.mapped_as_dataclass
class User:
    """Modelo de usuário representando a tabela 'users' no banco de dados."""

    __tablename__ = 'users'  # Nome da tabela no banco de dados

    # Colunas da tabela:
    id: Mapped[int] = mapped_column(init=False, primary_key=True)  # ID autoincremental
    username: Mapped[str] = mapped_column(unique=True)  # Nome de usuário único
    password: Mapped[str]  # Senha do usuário
    email: Mapped[str] = mapped_column(unique=True)  # Email único do usuário

    # Timestamps automáticos:
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),  # Data de criação automática
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),  # Data de atualização automática
    )


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
