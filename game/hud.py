from __future__ import annotations

from engine.core.math import Color, Vector2
from engine.scene.node_2d.node_2d import Node2D


class HUD(Node2D):
    def __init__(self, board_width: int):
        super().__init__("HUD")
        self.score: int = 0
        self.game_over: bool = False
        self._board_width = board_width
        self.z_index = 10

    def set_score(self, score: int):
        self.score = score

    def set_game_over(self, game_over: bool):
        self.game_over = game_over

    def _draw(self):
        self.draw_text(
            f"Score: {self.score}",
            Vector2(10, 5),
            Color.WHITE,
            font_size=22,
        )
        if self.game_over:
            self.draw_text(
                "GAME OVER",
                Vector2(self._board_width // 2 - 70, 200),
                Color.RED,
                font_size=32,
            )
            self.draw_text(
                "Press R to restart",
                Vector2(self._board_width // 2 - 100, 240),
                Color.WHITE,
                font_size=20,
            )
