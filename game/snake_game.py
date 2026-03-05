from __future__ import annotations

from engine.core.math import Vector2
from engine.input.input_event import InputEvent, InputEventKey
from engine.scene.node_2d.node_2d import Node2D
from game.food import Food
from game.game_board import GameBoard
from game.hud import HUD
from game.snake_body import SnakeBody
from game.snake_head import SnakeHead


COLS = 20
ROWS = 20
CELL_SIZE = 25
HUD_HEIGHT = 35


class SnakeGame(Node2D):
    def __init__(self):
        super().__init__("SnakeGame")
        self.board: GameBoard | None = None
        self.snake: SnakeHead | None = None
        self.food: Food | None = None
        self.hud: HUD | None = None
        self.score = 0
        self._game_over = False

    def _ready(self):
        self._setup_game()

    def _setup_game(self):
        # Clear existing children
        for child in list(self.get_children()):
            self.remove_child(child)

        self.score = 0
        self._game_over = False

        # Board is offset down by HUD height
        self.board = GameBoard(COLS, ROWS, CELL_SIZE)
        self.board.position = Vector2(0, HUD_HEIGHT)
        self.add_child(self.board)

        # Snake starts in the middle
        start_pos = Vector2(COLS // 2, ROWS // 2)
        self.snake = SnakeHead(start_pos, CELL_SIZE, COLS, ROWS)
        self.add_child(self.snake)

        # Food
        self.food = Food(COLS, ROWS, CELL_SIZE)
        self.add_child(self.food)
        self.food.spawn(self.snake.get_all_positions())

        # HUD
        self.hud = HUD(COLS * CELL_SIZE)
        self.add_child(self.hud)

    def check_food_collision(self, head_pos: Vector2):
        if head_pos == self.food.grid_pos:
            self.score += 1
            self.hud.set_score(self.score)
            self.snake.grow()
            self.food.spawn(self.snake.get_all_positions())

    def on_game_over(self):
        self._game_over = True
        self.hud.set_game_over(True)

    def _input(self, event: InputEvent):
        if isinstance(event, InputEventKey) and event.is_action_pressed("restart"):
            if self._game_over:
                self._setup_game()
