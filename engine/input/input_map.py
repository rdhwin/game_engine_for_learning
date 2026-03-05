from __future__ import annotations

from engine.input.input_event import InputEventKey


class InputMap:
    _instance: InputMap | None = None

    def __init__(self):
        self._actions: dict[str, list[int]] = {}

    @classmethod
    def get_singleton(cls) -> InputMap:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_action(self, action: str):
        if action not in self._actions:
            self._actions[action] = []

    def action_add_event(self, action: str, keycode: int):
        if action not in self._actions:
            self.add_action(action)
        self._actions[action].append(keycode)

    def event_is_action(self, event: InputEventKey, action: str) -> bool:
        if action not in self._actions:
            return False
        return event.keycode in self._actions[action]

    def get_actions(self) -> list[str]:
        return list(self._actions.keys())
