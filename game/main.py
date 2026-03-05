import pygame

from engine.engine import Engine
from engine.input.input_map import InputMap
from game.snake_game import SnakeGame, COLS, ROWS, CELL_SIZE, HUD_HEIGHT


def configure_input():
    input_map = InputMap.get_singleton()

    input_map.add_action("move_up")
    input_map.action_add_event("move_up", pygame.K_w)
    input_map.action_add_event("move_up", pygame.K_UP)

    input_map.add_action("move_down")
    input_map.action_add_event("move_down", pygame.K_s)
    input_map.action_add_event("move_down", pygame.K_DOWN)

    input_map.add_action("move_left")
    input_map.action_add_event("move_left", pygame.K_a)
    input_map.action_add_event("move_left", pygame.K_LEFT)

    input_map.add_action("move_right")
    input_map.action_add_event("move_right", pygame.K_d)
    input_map.action_add_event("move_right", pygame.K_RIGHT)

    input_map.add_action("restart")
    input_map.action_add_event("restart", pygame.K_r)


def main():
    configure_input()

    width = COLS * CELL_SIZE
    height = ROWS * CELL_SIZE + HUD_HEIGHT

    engine = Engine(
        title="Snake - Mini-Godot Engine",
        width=width,
        height=height,
        fps=60,
        physics_fps=10,
    )

    engine.run(SnakeGame())


if __name__ == "__main__":
    main()
