from __future__ import annotations

from engine.core.math import Color, Rect2, Vector2
from engine.scene.node_2d.node_2d import Node2D


class GameBoard(Node2D):
    def __init__(self, cols: int, rows: int, cell_size: int):
        super().__init__("GameBoard")
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.z_index = 0

    def get_pixel_pos(self, grid_pos: Vector2) -> Vector2:
        gp = self.get_global_position()
        return Vector2(
            gp.x + grid_pos.x * self.cell_size,
            gp.y + grid_pos.y * self.cell_size,
        )

    def _draw(self):
        bg_color = Color(0.1, 0.1, 0.1)
        line_color = Color(0.18, 0.18, 0.18)
        border_color = Color(0.4, 0.4, 0.4)

        # Background
        total_w = self.cols * self.cell_size
        total_h = self.rows * self.cell_size
        self.draw_rect(
            Rect2(Vector2(), Vector2(total_w, total_h)),
            bg_color,
        )

        # Grid lines
        for x in range(1, self.cols):
            self.draw_line(
                Vector2(x * self.cell_size, 0),
                Vector2(x * self.cell_size, total_h),
                line_color,
            )
        for y in range(1, self.rows):
            self.draw_line(
                Vector2(0, y * self.cell_size),
                Vector2(total_w, y * self.cell_size),
                line_color,
            )

        # Border
        self.draw_rect(
            Rect2(Vector2(), Vector2(total_w, total_h)),
            border_color,
            filled=False,
            width=2,
        )
