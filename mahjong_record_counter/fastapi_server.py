import json
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pywebio.platform.fastapi import webio_routes

from mahjong_record_counter.pywebio_task_func import pywebio_task_func

app = FastAPI()

security = HTTPBasic()


def read_json_file():
    with open("common_players.json", "r") as file:
        data = json.load(file)
    return data


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, os.getenv("USERNAME")
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.getenv("PASSWORD")
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


@app.get("/common_players", dependencies=[Depends(authenticate)])
def get_common_players():
    data = read_json_file()
    return data


app.mount("/", FastAPI(routes=webio_routes(pywebio_task_func)))


def run_server():

    import uvicorn

    debug = os.environ.get("DEBUG", "False")
    if debug == "True":
        uvicorn.run(
            "mahjong_record_counter.fastapi_server:app",
            host="0.0.0.0",
            port=8080,
            reload=True,
            env_file=".env.dev",
        )
    else:
        uvicorn.run(
            "mahjong_record_counter.fastapi_server:app",
            host="0.0.0.0",
            port=os.getenv("COUNT_POINT_PORT"),
            env_file=".env.prod",
        )
