from __future__ import annotations

from engine.core.math import Color, Rect2, Vector2
from engine.input.input_event import InputEvent
from engine.scene.node_2d.node_2d import Node2D
from game.snake_body import SnakeBody


class SnakeHead(Node2D):
    def __init__(self, grid_pos: Vector2, cell_size: int, cols: int, rows: int):
        super().__init__("SnakeHead")
        self.grid_pos = grid_pos.copy()
        self.prev_grid_pos = grid_pos.copy()
        self.cell_size = cell_size
        self.cols = cols
        self.rows = rows
        self.direction = Vector2.RIGHT
        self._buffered_direction: Vector2 | None = None
        self.body_segments: list[SnakeBody] = []
        self.z_index = 2
        self._grow_pending = False
        self._color = Color(0.0, 0.9, 0.0)
        self._game_over = False

    def _input(self, event: InputEvent):
        if self._game_over:
            return

        from engine.input.input_event import InputEventKey
        if not isinstance(event, InputEventKey) or not event.pressed:
            return

        new_dir = None
        if event.is_action_pressed("move_up"):
            new_dir = Vector2.UP
        elif event.is_action_pressed("move_down"):
            new_dir = Vector2.DOWN
        elif event.is_action_pressed("move_left"):
            new_dir = Vector2.LEFT
        elif event.is_action_pressed("move_right"):
            new_dir = Vector2.RIGHT

        # Prevent reversing into self
        if new_dir and not (new_dir + self.direction == Vector2.ZERO):
            self._buffered_direction = new_dir

    def _physics_process(self, delta: float):
        if self._game_over:
            return

        # Apply buffered direction
        if self._buffered_direction is not None:
            self.direction = self._buffered_direction
            self._buffered_direction = None

        # Save previous position
        self.prev_grid_pos = self.grid_pos.copy()

        # Move
        self.grid_pos = self.grid_pos + self.direction

        # Wall collision
        if (self.grid_pos.x < 0 or self.grid_pos.x >= self.cols
                or self.grid_pos.y < 0 or self.grid_pos.y >= self.rows):
            self._trigger_game_over()
            return

        # Self collision
        for seg in self.body_segments:
            if self.grid_pos == seg.grid_pos:
                self._trigger_game_over()
                return

        # Move body segments
        self._move_body()

        # Check food
        snake_game = self._get_snake_game()
        if snake_game:
            snake_game.check_food_collision(self.grid_pos)

    def _move_body(self):
        if not self.body_segments:
            return

        # Move from tail to head: each segment takes the position of the one ahead
        for i in range(len(self.body_segments) - 1, 0, -1):
            self.body_segments[i].prev_grid_pos = self.body_segments[i].grid_pos.copy()
            self.body_segments[i].grid_pos = self.body_segments[i - 1].grid_pos.copy()

        self.body_segments[0].prev_grid_pos = self.body_segments[0].grid_pos.copy()
        self.body_segments[0].grid_pos = self.prev_grid_pos.copy()

    def grow(self):
        # Add a new segment at the tail's previous position
        if self.body_segments:
            pos = self.body_segments[-1].prev_grid_pos.copy()
        else:
            pos = self.prev_grid_pos.copy()
        seg = SnakeBody(pos, self.cell_size, len(self.body_segments))
        self.body_segments.append(seg)
        # Add as child of the snake game node so it renders
        snake_game = self._get_snake_game()
        if snake_game:
            snake_game.add_child(seg)

    def get_all_positions(self) -> list[Vector2]:
        positions = [self.grid_pos.copy()]
        for seg in self.body_segments:
            positions.append(seg.grid_pos.copy())
        return positions

    def _trigger_game_over(self):
        self._game_over = True
        snake_game = self._get_snake_game()
        if snake_game:
            snake_game.on_game_over()

    def _get_snake_game(self):
        from game.snake_game import SnakeGame
        p = self.get_parent()
        while p is not None:
            if isinstance(p, SnakeGame):
                return p
            p = p.get_parent()
        return None

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
            # Try getting from snake_game
            snake_game = self._get_snake_game()
            if snake_game:
                game_board = snake_game.board
        if game_board is None:
            return

        pixel_pos = game_board.get_pixel_pos(self.grid_pos)
        padding = 1
        self.draw_rect(
            Rect2(
                Vector2(pixel_pos.x + padding - self.get_global_position().x,
                        pixel_pos.y + padding - self.get_global_position().y),
                Vector2(self.cell_size - padding * 2, self.cell_size - padding * 2),
            ),
            self._color,
        )
