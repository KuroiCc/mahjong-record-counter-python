import os
from typing import Optional

from pywebio import start_server
from pywebio.input import NUMBER, TEXT, input, input_group, select
from pywebio.output import put_button, put_html, put_row, put_text, use_scope, toast
from pywebio.pin import pin, put_input, pin_update
from pywebio.session import eval_js

from mahjong_record_counter.interface import GameSetting, PlayerRecord
from mahjong_record_counter.service import MahjongRecordCounterService


def make_option(
    label: str,
    value: object,
    selected: Optional[bool] = None,
    disabled: Optional[bool] = None,
):
    return {
        "label": label,
        "value": value,
        "selected": selected,
        "disabled": disabled,
    }


js_helper = {}
with open("./mahjong_record_counter/js_helper/fetchCommonPlayers.js", "r") as f:
    js_helper["fetchCommonPlayers"] = f.read()


def pywebio_task_func():
    login_intent = eval_js("new URLSearchParams(location.search).get('wantLogin')")
    common_players = None
    print(f"{login_intent=}")

    if login_intent == "yes":
        common_players = eval_js(
            js_helper["fetchCommonPlayers"],
            url=f"{os.getenv('COUNT_POINT_ROOT_PATH', '')}/common_players",
        )
        if not isinstance(common_players, list) or len(common_players) == 0:
            common_players = None

    # * page1: game setting
    setting_raw = input_group(
        label="rule",
        inputs=[
            input(name="start", label="スタート", type=NUMBER, value=25000),
            input(name="return_", label="返し", type=NUMBER, value=30000),
            select(
                name="uma",
                label="\nうま",
                options=[
                    make_option("うまなし", [0, 0]),
                    make_option("ゴットー(5-10)", [5, 10]),
                    make_option("ワンツー(10-20)", [10, 20]),
                    make_option("ワンスリー(10-30)", [10, 30], selected=True),
                    make_option("ツースリー(20-30", [20, 30]),
                ],
            ),
            input(name="score_scale", label="点数スケーリング", type=NUMBER, value=100),
        ],
    )

    # * page2: score calculation
    game_service = MahjongRecordCounterService(
        GameSetting(
            start=setting_raw["start"],
            return_=setting_raw["return_"],
            uma=setting_raw["uma"],
            score_scale=setting_raw["score_scale"],
        )
    )
    cf = game_service.game_setting

    with use_scope("setting"):
        put_html("<h1>設定</h1>")
        put_text(
            f"{cf.start}の{cf.return_}返し\nウマは{cf.uma[0]}-{cf.uma[1]}、オカアリ"
        )

    position_ind_name = list(enumerate(game_service.player_positions))
    for ind, name in position_ind_name:
        put_row(
            [
                put_input(
                    name=f"{ind}_name",
                    label=f"{name}家:",
                    type=TEXT,
                    datalist=common_players if common_players else None,
                ),
                None,
                put_input(
                    name=f"{ind}_score",
                    label="点数:",
                    type=NUMBER,
                ),
            ],
            size="3fr 10px 7fr",
        )

    put_button(label="追加", onclick=lambda: add_score())
    put_html("<h1>スコア</h1>")

    def add_score():
        if not all(
            [
                *[pin[f"{ind}_name"] for ind, _ in position_ind_name],
                *[pin[f"{ind}_score"] for ind, _ in position_ind_name],
            ],
        ):
            toast("全てのプレイヤーの名前と点数を入力してください", color="warn")
            return
        res_text = game_service.calculate_score(
            [
                PlayerRecord(
                    player_name=pin[f"{ind}_name"],
                    score=pin[f"{ind}_score"],
                    position=position,
                )
                for ind, position in position_ind_name
            ]
        )
        with use_scope("score"):
            put_text(res_text)

        for ind, _ in position_ind_name:
            pin_update(f"{ind}_score", value="")


def run():
    debug = os.environ.get("DEBUG", "False")
    if debug == "True":
        start_server(pywebio_task_func, port=8080, debug=True)
    else:
        start_server(
            pywebio_task_func,
            port=os.getenv("COUNT_POINT_PORT"),
            allowed_origins=["*"],
        )


if __name__ == "__main__":
    run()
