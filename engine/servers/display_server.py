from __future__ import annotations

import pygame

from engine.core.math import Vector2
from engine.input.input_event import InputEventKey


class DisplayServer:
    _instance: DisplayServer | None = None

    def __init__(self):
        self._surface: pygame.Surface | None = None
        self._clock: pygame.time.Clock | None = None

    @classmethod
    def get_singleton(cls) -> DisplayServer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, title: str, width: int, height: int) -> pygame.Surface:
        pygame.init()
        self._surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self._clock = pygame.time.Clock()
        return self._surface

    def get_surface(self) -> pygame.Surface:
        return self._surface

    def get_clock(self) -> pygame.time.Clock:
        return self._clock

    def poll_events(self) -> list:
        events = []
        for pg_event in pygame.event.get():
            if pg_event.type == pygame.QUIT:
                events.append(("quit", None))
            elif pg_event.type == pygame.KEYDOWN:
                events.append((
                    "input",
                    InputEventKey(pg_event.key, pressed=True, echo=False),
                ))
            elif pg_event.type == pygame.KEYUP:
                events.append((
                    "input",
                    InputEventKey(pg_event.key, pressed=False, echo=False),
                ))
        return events

    def finalize(self):
        pygame.quit()
