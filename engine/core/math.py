from __future__ import annotations


class Vector2:
    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        return self.__mul__(scalar)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def copy(self) -> Vector2:
        return Vector2(self.x, self.y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def to_int_tuple(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))


Vector2.ZERO = Vector2(0, 0)
Vector2.UP = Vector2(0, -1)
Vector2.DOWN = Vector2(0, 1)
Vector2.LEFT = Vector2(-1, 0)
Vector2.RIGHT = Vector2(1, 0)


class Color:
    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def to_pygame(self) -> tuple[int, int, int, int]:
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255),
        )

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


Color.WHITE = Color(1, 1, 1)
Color.BLACK = Color(0, 0, 0)
Color.RED = Color(1, 0, 0)
Color.GREEN = Color(0, 1, 0)
Color.BLUE = Color(0, 0, 1)
Color.YELLOW = Color(1, 1, 0)
Color.GRAY = Color(0.5, 0.5, 0.5)
Color.DARK_GRAY = Color(0.2, 0.2, 0.2)


class Rect2:
    __slots__ = ("position", "size")

    def __init__(self, position: Vector2 = None, size: Vector2 = None):
        self.position = position if position else Vector2()
        self.size = size if size else Vector2()

    @staticmethod
    def from_values(x: float, y: float, w: float, h: float) -> Rect2:
        return Rect2(Vector2(x, y), Vector2(w, h))

    def intersects(self, other: Rect2) -> bool:
        return (
            self.position.x < other.position.x + other.size.x
            and self.position.x + self.size.x > other.position.x
            and self.position.y < other.position.y + other.size.y
            and self.position.y + self.size.y > other.position.y
        )

    def to_pygame(self) -> tuple[int, int, int, int]:
        return (
            int(self.position.x),
            int(self.position.y),
            int(self.size.x),
            int(self.size.y),
        )

    def __repr__(self) -> str:
        return f"Rect2({self.position}, {self.size})"
