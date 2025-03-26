from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def hello_world():
    return {'Hello': 'World'}


@app.get('/{name}')
def hello_name(name: str):
    return {'Hello': name}
