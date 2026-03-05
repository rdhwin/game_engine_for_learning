from __future__ import annotations

from engine.core.math import Color, Rect2, Vector2
from engine.scene.main.node import Node
from engine.servers.rendering_server import RenderingServer


class CanvasItem(Node):
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.visible: bool = True
        self.z_index: int = 0
        self._needs_redraw: bool = True

    def queue_redraw(self):
        self._needs_redraw = True

    def _do_draw(self):
        if self.visible:
            self._draw()
            self._needs_redraw = False

    def _draw(self):
        pass

    # --- Draw helpers that delegate to RenderingServer ---

    def _get_draw_offset(self) -> Vector2:
        return Vector2.ZERO

    def draw_rect(self, rect: Rect2, color: Color, filled: bool = True, width: int = 1):
        offset = self._get_draw_offset()
        offset_rect = Rect2(rect.position + offset, rect.size)
        RenderingServer.get_singleton().draw_rect(offset_rect, color, filled, width)

    def draw_circle(self, center: Vector2, radius: float, color: Color, filled: bool = True, width: int = 1):
        offset = self._get_draw_offset()
        RenderingServer.get_singleton().draw_circle(center + offset, radius, color, filled, width)

    def draw_line(self, start: Vector2, end: Vector2, color: Color, width: int = 1):
        offset = self._get_draw_offset()
        RenderingServer.get_singleton().draw_line(start + offset, end + offset, color, width)

    def draw_text(self, text: str, position: Vector2, color: Color, font_size: int = 20):
        offset = self._get_draw_offset()
        RenderingServer.get_singleton().draw_text(text, position + offset, color, font_size)
