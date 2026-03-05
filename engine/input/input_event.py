from __future__ import annotations


class InputEvent:
    pass


class InputEventKey(InputEvent):
    def __init__(self, keycode: int, pressed: bool, echo: bool = False):
        self.keycode = keycode
        self.pressed = pressed
        self.echo = echo

    def is_pressed(self) -> bool:
        return self.pressed

    def is_released(self) -> bool:
        return not self.pressed

    def is_echo(self) -> bool:
        return self.echo

    def is_action(self, action: str) -> bool:
        from engine.input.input_map import InputMap
        return InputMap.get_singleton().event_is_action(self, action)

    def is_action_pressed(self, action: str) -> bool:
        return self.is_action(action) and self.pressed and not self.echo

    def is_action_released(self, action: str) -> bool:
        return self.is_action(action) and not self.pressed
