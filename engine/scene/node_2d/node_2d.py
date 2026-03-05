from __future__ import annotations

from engine.core.math import Vector2
from engine.scene.node_2d.canvas_item import CanvasItem


class Node2D(CanvasItem):
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.position: Vector2 = Vector2()
        self.rotation: float = 0.0
        self.scale: Vector2 = Vector2(1, 1)

    def get_global_position(self) -> Vector2:
        pos = self.position.copy()
        parent = self._parent
        while parent is not None:
            if isinstance(parent, Node2D):
                pos = pos + parent.position
            parent = parent._parent
        return pos

    def _get_draw_offset(self) -> Vector2:
        return self.get_global_position()
