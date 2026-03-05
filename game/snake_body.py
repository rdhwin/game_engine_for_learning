from __future__ import annotations

from engine.core.math import Color, Rect2, Vector2
from engine.scene.node_2d.node_2d import Node2D


class SnakeBody(Node2D):
    def __init__(self, grid_pos: Vector2, cell_size: int, index: int = 0):
        super().__init__(f"SnakeBody_{index}")
        self.grid_pos = grid_pos.copy()
        self.prev_grid_pos = grid_pos.copy()
        self.cell_size = cell_size
        self.z_index = 1
        self._color = Color(0.0, 0.75, 0.0)

    def _draw(self):
        board = self.get_parent()
        if board is None:
            return
        # Get pixel position from parent board
        from game.game_board import GameBoard
        game_board = None
        p = self.get_parent()
        while p is not None:
            if isinstance(p, GameBoard):
                game_board = p
                break
            p = p.get_parent()
        if game_board is None:
            return

        pixel_pos = game_board.get_pixel_pos(self.grid_pos)
        # Draw relative to our Node2D global position offset = 0,0 since we're direct child of board owner
        padding = 2
        self.draw_rect(
            Rect2(
                Vector2(pixel_pos.x + padding - self.get_global_position().x,
                        pixel_pos.y + padding - self.get_global_position().y),
                Vector2(self.cell_size - padding * 2, self.cell_size - padding * 2),
            ),
            self._color,
        )
