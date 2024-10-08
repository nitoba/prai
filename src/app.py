from fastapi import FastAPI

from src.env import env

app = FastAPI()


@app.get('/')
def read_root():
    return {'data': env}
