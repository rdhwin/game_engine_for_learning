from __future__ import annotations

from engine.core.main_loop import MainLoop
from engine.input.input_event import InputEvent
from engine.scene.main.node import Node
from engine.scene.node_2d.canvas_item import CanvasItem


class SceneTree(MainLoop):
    _instance: SceneTree | None = None

    def __init__(self):
        self.root: Node = Node("root")
        self._current_scene: Node | None = None
        self._quit_requested: bool = False
        self._delete_queue: list[Node] = []

    @classmethod
    def get_singleton(cls) -> SceneTree:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self):
        self.root._propagate_enter_tree(self)
        self.root._propagate_ready()

    def set_current_scene(self, scene: Node):
        if self._current_scene is not None:
            self.root.remove_child(self._current_scene)
        self._current_scene = scene
        self.root.add_child(scene)

    def quit(self):
        self._quit_requested = True

    def is_quit_requested(self) -> bool:
        return self._quit_requested

    def queue_delete(self, node: Node):
        if node not in self._delete_queue:
            self._delete_queue.append(node)

    def flush_delete_queue(self):
        for node in self._delete_queue:
            parent = node.get_parent()
            if parent:
                parent.remove_child(node)
        self._delete_queue.clear()

    # --- Process ---

    def propagate_input(self, event: InputEvent):
        self.root._propagate_input(event)

    def process(self, delta: float):
        self.root._propagate_process(delta)

    def physics_process(self, delta: float):
        self.root._propagate_physics_process(delta)

    # --- Draw ---

    def draw(self):
        canvas_items = self._collect_canvas_items(self.root)
        canvas_items.sort(key=lambda ci: ci.z_index)
        for item in canvas_items:
            item._do_draw()

    def _collect_canvas_items(self, node: Node) -> list[CanvasItem]:
        items: list[CanvasItem] = []
        if isinstance(node, CanvasItem):
            items.append(node)
        for child in node.get_children():
            items.extend(self._collect_canvas_items(child))
        return items

    def finalize(self):
        self.root._propagate_exit_tree()
