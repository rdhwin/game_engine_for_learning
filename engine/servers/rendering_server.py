from __future__ import annotations

import pygame

from engine.core.math import Color, Rect2, Vector2


class RenderingServer:
    _instance: RenderingServer | None = None

    def __init__(self):
        self._surface: pygame.Surface | None = None
        self._font: pygame.font.Font | None = None

    @classmethod
    def get_singleton(cls) -> RenderingServer:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, surface: pygame.Surface):
        self._surface = surface
        pygame.font.init()
        self._font = pygame.font.SysFont("monospace", 20)

    def clear(self, color: Color):
        self._surface.fill(color.to_pygame())

    def draw_rect(self, rect: Rect2, color: Color, filled: bool = True, width: int = 1):
        if filled:
            pygame.draw.rect(self._surface, color.to_pygame(), rect.to_pygame())
        else:
            pygame.draw.rect(self._surface, color.to_pygame(), rect.to_pygame(), width)

    def draw_circle(self, center: Vector2, radius: float, color: Color, filled: bool = True, width: int = 1):
        if filled:
            pygame.draw.circle(self._surface, color.to_pygame(), center.to_int_tuple(), int(radius))
        else:
            pygame.draw.circle(self._surface, color.to_pygame(), center.to_int_tuple(), int(radius), width)

    def draw_line(self, start: Vector2, end: Vector2, color: Color, width: int = 1):
        pygame.draw.line(self._surface, color.to_pygame(), start.to_int_tuple(), end.to_int_tuple(), width)

    def draw_text(self, text: str, position: Vector2, color: Color, font_size: int = 20):
        if self._font.get_height() != font_size:
            font = pygame.font.SysFont("monospace", font_size)
        else:
            font = self._font
        text_surface = font.render(text, True, color.to_pygame()[:3])
        self._surface.blit(text_surface, position.to_int_tuple())

    def present(self):
        pygame.display.flip()
