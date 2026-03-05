from __future__ import annotations

from engine.core.math import Color
from engine.input.input import Input
from engine.input.input_map import InputMap
from engine.scene.main.node import Node
from engine.scene.main.scene_tree import SceneTree
from engine.servers.display_server import DisplayServer
from engine.servers.rendering_server import RenderingServer


class Engine:
    def __init__(self, title: str = "Mini-Godot", width: int = 640, height: int = 480,
                 fps: int = 60, physics_fps: int = 10):
        self._title = title
        self._width = width
        self._height = height
        self._fps = fps
        self._physics_fps = physics_fps
        self._physics_delta = 1.0 / physics_fps

        self._display_server = DisplayServer.get_singleton()
        self._rendering_server = RenderingServer.get_singleton()
        self._input = Input.get_singleton()
        self._input_map = InputMap.get_singleton()
        self._scene_tree = SceneTree.get_singleton()

    def run(self, root_scene: Node):
        surface = self._display_server.initialize(self._title, self._width, self._height)
        self._rendering_server.initialize(surface)
        self._scene_tree.initialize()
        self._scene_tree.set_current_scene(root_scene)

        clock = self._display_server.get_clock()
        physics_accumulator = 0.0

        while not self._scene_tree.is_quit_requested():
            # Delta in seconds
            delta_ms = clock.tick(self._fps)
            delta = delta_ms / 1000.0

            # Poll events
            events = self._display_server.poll_events()

            # Check for quit
            for event_type, event_data in events:
                if event_type == "quit":
                    self._scene_tree.quit()
                    break

            if self._scene_tree.is_quit_requested():
                break

            # Update input state
            self._input.update(events)

            # Propagate input events
            for event_type, event_data in events:
                if event_type == "input":
                    self._scene_tree.propagate_input(event_data)

            # Fixed-timestep physics
            physics_accumulator += delta
            while physics_accumulator >= self._physics_delta:
                self._scene_tree.physics_process(self._physics_delta)
                physics_accumulator -= self._physics_delta

            # Process
            self._scene_tree.process(delta)

            # Render
            self._rendering_server.clear(Color.BLACK)
            self._scene_tree.draw()
            self._rendering_server.present()

            # Cleanup
            self._scene_tree.flush_delete_queue()

        self._scene_tree.finalize()
        self._display_server.finalize()
