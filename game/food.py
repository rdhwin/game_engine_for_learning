from __future__ import annotations

import random

from engine.core.math import Color, Rect2, Vector2
from engine.scene.node_2d.node_2d import Node2D


class Food(Node2D):
    def __init__(self, cols: int, rows: int, cell_size: int):
        super().__init__("Food")
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.grid_pos = Vector2()
        self.z_index = 1
        self._color = Color(1.0, 0.2, 0.2)

    def spawn(self, occupied: list[Vector2]):
        occupied_set = {(int(p.x), int(p.y)) for p in occupied}
        available = []
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) not in occupied_set:
                    available.append(Vector2(x, y))
        if available:
            self.grid_pos = random.choice(available)

    def _draw(self):
        from game.game_board import GameBoard
        game_board = None
        p = self.get_parent()
        while p is not None:
            if isinstance(p, GameBoard):
                game_board = p
                break
            p = p.get_parent()
        if game_board is None:
            from game.snake_game import SnakeGame
            sg = self.get_parent()
            while sg is not None:
                if isinstance(sg, SnakeGame):
                    game_board = sg.board
                    break
                sg = sg.get_parent()
        if game_board is None:
            return

        pixel_pos = game_board.get_pixel_pos(self.grid_pos)
        center = Vector2(
            pixel_pos.x + self.cell_size / 2 - self.get_global_position().x,
            pixel_pos.y + self.cell_size / 2 - self.get_global_position().y,
        )
        self.draw_circle(center, self.cell_size / 2 - 3, self._color)
