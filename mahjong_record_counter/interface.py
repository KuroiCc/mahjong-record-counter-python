import typing as t

from pydantic import BaseModel


class GameSetting(BaseModel):
    start: int
    return_: int
    uma: list[int, int]
    score_scale: int = 1


class PlayerRecord(BaseModel):
    player_name: str
    score: int
    position: t.Literal["東", "南", "西", "北"]
    rank: int | None = None
    pt: float | None = None
