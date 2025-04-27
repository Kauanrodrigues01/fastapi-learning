from fastapi import FastAPI

from fast_zero.routers import auth, users

app = FastAPI(
    debug=True,
    title='Aula - Tornando o sistema de autenticação mais robusto',
    description='Aprendendo a utilizar routers, annotated e reorganizar o projeto.',
    version='0.1.0',
)
app.include_router(users.router)
app.include_router(auth.router)
