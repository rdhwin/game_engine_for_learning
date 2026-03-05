from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.input.input_event import InputEvent
    from engine.scene.main.scene_tree import SceneTree


class Node:
    def __init__(self, name: str = ""):
        self.name: str = name or self.__class__.__name__
        self._parent: Node | None = None
        self._children: list[Node] = []
        self._tree: SceneTree | None = None
        self._inside_tree: bool = False
        self._ready_called: bool = False
        self._process_enabled: bool = True
        self._physics_process_enabled: bool = True
        self._input_enabled: bool = True
        self._queued_for_deletion: bool = False

    # --- Tree operations ---

    def add_child(self, child: Node):
        child._parent = self
        self._children.append(child)
        if self._inside_tree:
            child._propagate_enter_tree(self._tree)
            child._propagate_ready()

    def remove_child(self, child: Node):
        if child in self._children:
            if child._inside_tree:
                child._propagate_exit_tree()
            child._parent = None
            self._children.remove(child)

    def get_parent(self) -> Node | None:
        return self._parent

    def get_children(self) -> list[Node]:
        return list(self._children)

    def get_child_count(self) -> int:
        return len(self._children)

    def get_node(self, path: str) -> Node | None:
        parts = path.strip("/").split("/")
        current = self
        for part in parts:
            found = None
            for child in current._children:
                if child.name == part:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current

    def get_tree(self) -> SceneTree | None:
        return self._tree

    def is_inside_tree(self) -> bool:
        return self._inside_tree

    # --- Lifecycle propagation ---

    def _propagate_enter_tree(self, tree: SceneTree):
        self._tree = tree
        self._inside_tree = True
        self._enter_tree()
        for child in self._children:
            child._propagate_enter_tree(tree)

    def _propagate_ready(self):
        for child in self._children:
            if not child._ready_called:
                child._propagate_ready()
        if not self._ready_called:
            self._ready_called = True
            self._ready()

    def _propagate_exit_tree(self):
        for child in list(self._children):
            child._propagate_exit_tree()
        self._exit_tree()
        self._inside_tree = False
        self._tree = None

    # --- Process propagation ---

    def _propagate_process(self, delta: float):
        if self._process_enabled:
            self._process(delta)
        for child in self._children:
            child._propagate_process(delta)

    def _propagate_physics_process(self, delta: float):
        if self._physics_process_enabled:
            self._physics_process(delta)
        for child in self._children:
            child._propagate_physics_process(delta)

    def _propagate_input(self, event: InputEvent):
        if self._input_enabled:
            self._input(event)
        for child in self._children:
            child._propagate_input(event)

    # --- Flags ---

    def set_process(self, enabled: bool):
        self._process_enabled = enabled

    def set_physics_process(self, enabled: bool):
        self._physics_process_enabled = enabled

    def set_process_input(self, enabled: bool):
        self._input_enabled = enabled

    # --- Deferred deletion ---

    def queue_free(self):
        self._queued_for_deletion = True
        if self._tree:
            self._tree.queue_delete(self)

    # --- Virtual methods (override in subclasses) ---

    def _enter_tree(self):
        pass

    def _ready(self):
        pass

    def _exit_tree(self):
        pass

    def _process(self, delta: float):
        pass

    def _physics_process(self, delta: float):
        pass

    def _input(self, event: InputEvent):
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
