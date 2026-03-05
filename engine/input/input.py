from __future__ import annotations

from engine.input.input_event import InputEvent, InputEventKey
from engine.input.input_map import InputMap


class Input:
    _instance: Input | None = None

    def __init__(self):
        self._pressed_keys: set[int] = set()
        self._just_pressed_keys: set[int] = set()
        self._just_released_keys: set[int] = set()

    @classmethod
    def get_singleton(cls) -> Input:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update(self, events: list[tuple[str, InputEvent | None]]):
        self._just_pressed_keys.clear()
        self._just_released_keys.clear()
        for event_type, event in events:
            if event_type == "input" and isinstance(event, InputEventKey):
                if event.pressed:
                    if event.keycode not in self._pressed_keys:
                        self._just_pressed_keys.add(event.keycode)
                    self._pressed_keys.add(event.keycode)
                else:
                    self._pressed_keys.discard(event.keycode)
                    self._just_released_keys.add(event.keycode)

    def is_key_pressed(self, keycode: int) -> bool:
        return keycode in self._pressed_keys

    def is_action_pressed(self, action: str) -> bool:
        input_map = InputMap.get_singleton()
        for keycode in input_map._actions.get(action, []):
            if keycode in self._pressed_keys:
                return True
        return False

    def is_action_just_pressed(self, action: str) -> bool:
        input_map = InputMap.get_singleton()
        for keycode in input_map._actions.get(action, []):
            if keycode in self._just_pressed_keys:
                return True
        return False
