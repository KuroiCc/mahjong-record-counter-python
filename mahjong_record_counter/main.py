from typing import Optional
import os

from pywebio import start_server
from pywebio.input import NUMBER, checkbox, input, input_group, select
from pywebio.output import put_button, put_html, put_text, use_scope
from pywebio.pin import pin, put_input

import mahjong_record_counter.interface as IF


def make_option(
    label: str,
    value: object,
    selected: Optional[bool] = None,
    disabled: Optional[bool] = None,
):
    return {
        'label': label,
        'value': value,
        'selected': selected,
        'disabled': disabled,
    }


def main():
    setting_raw = input_group(
        label='rule',
        inputs=[
            input(name='start', label='スタート', type=NUMBER, value=25000),
            input(name='return_', label='返し', type=NUMBER, value=30000),
            select(
                name='uma',
                label='\nうま',
                options=[
                    make_option('ゴットー(5-10)', [5, 10]),
                    make_option('ワンツー(10-20)', [10, 20]),
                    make_option('ワンスリー(10-30)', [10, 30], selected=True),
                    make_option('ツースリー(20-30', [20, 30]),
                ],
            ),
            checkbox(
                name='oka',
                inline=True,
                options=[make_option('オカあり', True, selected=True)],
            ),
        ],
    )
    cf = IF.GameSetting(
        start=setting_raw['start'],
        return_=setting_raw['return_'],
        uma=setting_raw['uma'],
        oka=setting_raw['oka'][0],
    )
    with use_scope('setting'):
        put_html('<h1>設定</h1>')
        put_text(f'{cf.start}の{cf.return_}返し\nウマは{cf.uma[0]}-{cf.uma[1]}、オカアリ')

    put_input(name='no1', label='1番:', type=NUMBER)
    put_input(name='no2', label='2番:', type=NUMBER)
    put_input(name='no3', label='3番:', type=NUMBER)
    put_input(name='no4', label='4番:', type=NUMBER)
    put_button(label='追加', onclick=lambda: add_score(123))

    def add_score(score: list[int, int, int, int]):
        # TODO: オカなしに対応していない
        with use_scope('score'):
            put_html('<h1>スコア</h1>')
            put_text(
                (pin['no1'] - cf.return_ + (cf.return_ - cf.start) * 4) / 1000 + cf.uma[1],
                (pin['no2'] - cf.return_) / 1000 + cf.uma[0],
                (pin['no3'] - cf.return_) / 1000 - cf.uma[0],
                (pin['no4'] - cf.return_) / 1000 - cf.uma[1],
            )


def run():
    start_server(
        main,
        port=os.getenv('COUNT_POINT_PORT'),
        allowed_origins=['*'],
    )


if __name__ == '__main__':
    run()
