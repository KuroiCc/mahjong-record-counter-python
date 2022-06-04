from pydantic import BaseModel


class GameSetting(BaseModel):
    start: int
    return_: int
    uma: list[int, int]
    oka: bool
