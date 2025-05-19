from fastapi import FastAPI

from fast_zero.routers import auth, todos, users

app = FastAPI(
    debug=True,
    title='Aula - Dockerizando FastAPI',
    description='Criando e gerenciando tarefas',
    version='0.1.0',
)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)
