from mahjong_record_counter.interface import GameSetting, PlayerRecord


class MahjongRecordCounterService:
    def __init__(self, game_setting: GameSetting):
        self.game_setting = game_setting
        self.oka = (self.game_setting.return_ - self.game_setting.start) * 4 / 1000
        self.player_positions = ["東", "南", "西", "北"]

    def calculate_score(self, player_records: list[PlayerRecord]) -> str:
        if len(player_records) != 4:
            return "4人分の点数を入力してください"

        if (
            sum([pr.score for pr in player_records])
            != 100_000 / self.game_setting.score_scale
        ):
            return "合計が10万になるように点数を入力してください"

        if set([pr.position for pr in player_records]) != set(self.player_positions):
            return "東南西北の4人分のプレイヤーを入力してください"

        player_records.sort(
            key=lambda x: (-x.score, self.player_positions.index(x.position)),
        )
        for i, player_record in enumerate(player_records):
            player_record.rank = i + 1
            player_record.pt = self._get_score_pt(player_record.score)

        player_records[0].pt += self.game_setting.uma[1] + self.oka
        player_records[1].pt += self.game_setting.uma[0]
        player_records[2].pt += -self.game_setting.uma[0]
        player_records[3].pt += -self.game_setting.uma[1]

        return "  ".join(
            [f"{pr.player_name:<5}: {pr.pt:<7.1f}" for pr in player_records]
        )

    def _get_score_pt(self, score: int) -> float:
        score = score * self.game_setting.score_scale
        return (score - self.game_setting.return_) / 1000
