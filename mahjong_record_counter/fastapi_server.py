import json
import os
import secrets
from pathlib import Path

from fastapi import Body, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pywebio.platform.fastapi import webio_routes

from mahjong_record_counter.pywebio_task_func import pywebio_task_func

app = FastAPI(debug=bool(os.environ.get("DEBUG", "False")))


# MARK: - Service functions

data_store_path = Path("common_players.json")


def read_json_file() -> list[str]:
    with data_store_path.open("r") as file:
        data = json.load(file)
    return data


def add_common_player(player_name: str) -> list[str]:
    data = read_json_file()
    if player_name not in data:
        data.append(player_name)
    with data_store_path.open("w") as file:
        json.dump(data, file, ensure_ascii=False)

    return data


def remove_common_player(player_name: str) -> list[str] | None:
    data = read_json_file()

    if player_name not in data:
        return None

    data.remove(player_name)

    with data_store_path.open("w") as file:
        json.dump(data, file, ensure_ascii=False)

    return data


# MARK: - Dependency
security = HTTPBasic()


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


@app.middleware("http")
async def secure_docs(request: Request, call_next):
    if not app.debug and request.url.path in ["/docs", "/openapi.json"]:
        try:
            authenticate(await security(request))
        except HTTPException as exc:
            return PlainTextResponse(
                str(exc.detail),
                status_code=exc.status_code,
                headers=exc.headers,
            )

    return await call_next(request)


# MARK: - Routes
@app.get(
    "/common_players",
    dependencies=[Depends(authenticate)],
    response_model=list[str],
)
def get_common_players():
    data = read_json_file()
    return data


@app.put(
    "/common_players",
    dependencies=[Depends(authenticate)],
    response_model=list[str],
)
def put_common_player(player_name: str = Body(...)):
    data = add_common_player(player_name)
    return data


@app.delete(
    "/common_players/{player_name}",
    dependencies=[Depends(authenticate)],
    response_model=list[str],
)
def delete_common_player(player_name: str):
    data = remove_common_player(player_name)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    return data


app.mount("/", FastAPI(routes=webio_routes(pywebio_task_func)))


# MARK: - Run server
def run_server():

    import uvicorn

    if app.debug:
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
            port=int(os.getenv("COUNT_POINT_PORT")),
            env_file=".env.prod",
            root_path=os.getenv("COUNT_POINT_ROOT_PATH", ""),
        )
