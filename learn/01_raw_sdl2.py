"""
Layer 1: Raw SDL2 via ctypes — No Pygame, No Abstractions

This file opens a window, creates a pixel buffer, and draws directly to it
using SDL2's C API through Python's ctypes. This is what Pygame does under
the hood (Pygame is literally a Python wrapper around SDL2).

KEY CONCEPTS:
  1. SDL2 is a C library that talks to your OS's windowing system (Cocoa on Mac,
     X11/Wayland on Linux, Win32 on Windows) and your GPU.
  2. ctypes lets Python call C functions directly — we define the function
     signatures and struct layouts, then call them like normal Python functions.
  3. A "texture" is a block of memory (pixels) that lives on the GPU. We "lock"
     it to get a CPU-side pointer, write pixel data, then "unlock" to upload
     back to the GPU.
  4. Each pixel is 4 bytes: Alpha, Red, Green, Blue (ARGB8888 format).

RUN: python3 01_raw_sdl2.py
"""

import ctypes
import ctypes.util
import sys
import math

# =============================================================================
# STEP 1: Load the SDL2 shared library
# =============================================================================
# SDL2 is compiled C code sitting in a .dylib (Mac), .so (Linux), or .dll (Windows).
# ctypes.CDLL loads it into our process so we can call its functions.

sdl2 = ctypes.CDLL("/opt/homebrew/lib/libSDL2.dylib")

# =============================================================================
# STEP 2: Define SDL2 constants
# =============================================================================
# These are #define values from SDL2's C headers. We need them to tell SDL2
# what we want (e.g., "initialize video subsystem", "create a shown window").

# SDL_Init flags — which subsystems to start
SDL_INIT_VIDEO = 0x00000020
SDL_INIT_TIMER = 0x00000001

# Window position constants
SDL_WINDOWPOS_CENTERED = 0x2FFF0000

# Window flags
SDL_WINDOW_SHOWN = 0x00000004

# Renderer flags
SDL_RENDERER_ACCELERATED = 0x00000002  # Use GPU
SDL_RENDERER_PRESENTVSYNC = 0x00000004  # Sync to monitor refresh rate

# Pixel format — how bytes map to colors
# ARGB8888 = each pixel is 4 bytes: [Alpha][Red][Green][Blue]
SDL_PIXELFORMAT_ARGB8888 = 372645892

# Texture access modes
SDL_TEXTUREACCESS_STREAMING = 1  # We can lock/unlock to write pixels

# Event types — what kind of OS event happened
SDL_QUIT = 0x100           # User closed the window
SDL_KEYDOWN = 0x300        # Key was pressed
SDL_KEYUP = 0x301          # Key was released

# Scancodes (physical key positions)
SDL_SCANCODE_ESCAPE = 41
SDL_SCANCODE_SPACE = 44

# =============================================================================
# STEP 3: Define SDL2 structs using ctypes
# =============================================================================
# SDL2 uses C structs to pass data around. We need to mirror their memory
# layout exactly so ctypes can read/write them correctly.


class SDL_Rect(ctypes.Structure):
    """Rectangle: x, y, width, height — used for positioning and clipping."""
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("w", ctypes.c_int),
        ("h", ctypes.c_int),
    ]


class SDL_KeyboardEvent(ctypes.Structure):
    """Keyboard event data — which key, was it pressed or released, etc."""
    _fields_ = [
        ("type", ctypes.c_uint32),       # SDL_KEYDOWN or SDL_KEYUP
        ("timestamp", ctypes.c_uint32),  # When it happened (ms)
        ("windowID", ctypes.c_uint32),   # Which window
        ("state", ctypes.c_uint8),       # Pressed or released
        ("repeat", ctypes.c_uint8),      # Is this a key repeat?
        ("padding", ctypes.c_uint8 * 2), # Alignment padding
        ("scancode", ctypes.c_int32),    # Physical key code
        ("sym", ctypes.c_int32),         # Virtual key code
        ("mod", ctypes.c_uint16),        # Modifier keys (shift, ctrl, etc.)
    ]


class SDL_Event(ctypes.Union):
    """
    SDL_Event is a UNION — it can hold different event types in the same memory.
    The 'type' field tells you which variant to read. We allocate 56 bytes
    (the max size of any SDL event) so any event type fits.
    """
    _fields_ = [
        ("type", ctypes.c_uint32),
        ("key", SDL_KeyboardEvent),
        ("padding", ctypes.c_uint8 * 56),
    ]


# =============================================================================
# STEP 4: Declare SDL2 function signatures
# =============================================================================
# ctypes needs to know the return type and argument types of each C function.
# This is like writing function prototypes / header declarations.

# int SDL_Init(Uint32 flags)
sdl2.SDL_Init.argtypes = [ctypes.c_uint32]
sdl2.SDL_Init.restype = ctypes.c_int

# SDL_Window* SDL_CreateWindow(title, x, y, w, h, flags)
sdl2.SDL_CreateWindow.argtypes = [
    ctypes.c_char_p,  # title (C string)
    ctypes.c_int, ctypes.c_int,  # x, y position
    ctypes.c_int, ctypes.c_int,  # width, height
    ctypes.c_uint32,  # flags
]
sdl2.SDL_CreateWindow.restype = ctypes.c_void_p  # Returns opaque pointer

# SDL_Renderer* SDL_CreateRenderer(window, driver_index, flags)
sdl2.SDL_CreateRenderer.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint32]
sdl2.SDL_CreateRenderer.restype = ctypes.c_void_p

# SDL_Texture* SDL_CreateTexture(renderer, format, access, w, h)
sdl2.SDL_CreateTexture.argtypes = [
    ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
]
sdl2.SDL_CreateTexture.restype = ctypes.c_void_p

# int SDL_LockTexture(texture, rect*, pixels**, pitch*)
sdl2.SDL_LockTexture.argtypes = [
    ctypes.c_void_p,                          # texture
    ctypes.POINTER(SDL_Rect),                 # rect (NULL = whole texture)
    ctypes.POINTER(ctypes.c_void_p),          # out: pointer to pixel data
    ctypes.POINTER(ctypes.c_int),             # out: pitch (bytes per row)
]
sdl2.SDL_LockTexture.restype = ctypes.c_int

# void SDL_UnlockTexture(texture)
sdl2.SDL_UnlockTexture.argtypes = [ctypes.c_void_p]
sdl2.SDL_UnlockTexture.restype = None

# int SDL_RenderCopy(renderer, texture, src_rect*, dst_rect*)
sdl2.SDL_RenderCopy.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p,
    ctypes.POINTER(SDL_Rect), ctypes.POINTER(SDL_Rect),
]
sdl2.SDL_RenderCopy.restype = ctypes.c_int

# void SDL_RenderPresent(renderer) — flip the back buffer to screen
sdl2.SDL_RenderPresent.argtypes = [ctypes.c_void_p]
sdl2.SDL_RenderPresent.restype = None

# int SDL_PollEvent(event*) — returns 1 if event available, 0 if not
sdl2.SDL_PollEvent.argtypes = [ctypes.POINTER(SDL_Event)]
sdl2.SDL_PollEvent.restype = ctypes.c_int

# Uint32 SDL_GetTicks() — ms since SDL_Init
sdl2.SDL_GetTicks.argtypes = []
sdl2.SDL_GetTicks.restype = ctypes.c_uint32

# void SDL_Delay(ms) — sleep
sdl2.SDL_Delay.argtypes = [ctypes.c_uint32]
sdl2.SDL_Delay.restype = None

# Cleanup functions
sdl2.SDL_DestroyTexture.argtypes = [ctypes.c_void_p]
sdl2.SDL_DestroyRenderer.argtypes = [ctypes.c_void_p]
sdl2.SDL_DestroyWindow.argtypes = [ctypes.c_void_p]

# const char* SDL_GetError()
sdl2.SDL_GetError.argtypes = []
sdl2.SDL_GetError.restype = ctypes.c_char_p


# =============================================================================
# STEP 5: Helper — pack a color into a single 32-bit ARGB integer
# =============================================================================
def argb(r, g, b, a=255):
    """
    Pack RGBA values (0-255) into a single 32-bit integer.
    Memory layout: [AAAA AAAA][RRRR RRRR][GGGG GGGG][BBBB BBBB]
    This is how GPUs store pixel colors — one integer per pixel.
    """
    return (a << 24) | (r << 16) | (g << 8) | b


# =============================================================================
# STEP 6: Pixel buffer drawing functions
# =============================================================================
# These write directly to a raw memory buffer. This is the lowest level of
# 2D rendering — every draw call in Pygame eventually does something like this
# (or delegates to the GPU via OpenGL/Metal/Vulkan).

def set_pixel(pixels, pitch, x, y, color, width, height):
    """
    Set a single pixel in the buffer.

    pixels: pointer to the raw pixel memory (from SDL_LockTexture)
    pitch:  number of BYTES per row (may include padding for alignment)
    x, y:   pixel coordinates
    color:  32-bit ARGB value
    """
    if 0 <= x < width and 0 <= y < height:
        # Cast the raw pointer to a uint32 array so we can index by pixel
        row = ctypes.cast(
            ctypes.c_void_p(pixels + y * pitch),
            ctypes.POINTER(ctypes.c_uint32),
        )
        row[x] = color


def draw_rect_pixels(pixels, pitch, x, y, w, h, color, buf_w, buf_h, filled=True):
    """
    Draw a rectangle pixel by pixel.
    This is essentially what SDL_RenderFillRect does internally.
    """
    for py in range(max(0, y), min(y + h, buf_h)):
        for px in range(max(0, x), min(x + w, buf_w)):
            if filled or py == y or py == y + h - 1 or px == x or px == x + w - 1:
                set_pixel(pixels, pitch, px, py, color, buf_w, buf_h)


def draw_circle_pixels(pixels, pitch, cx, cy, radius, color, buf_w, buf_h, filled=True):
    """
    Draw a circle using the midpoint circle algorithm.

    The idea: instead of checking every pixel against x^2 + y^2 = r^2 (slow),
    we walk along the circle's edge and use an error term to decide whether
    to step in x or y. This is Bresenham's algorithm adapted for circles.
    """
    if filled:
        # Filled circle: for each row in the bounding box, draw the horizontal span
        for dy in range(-radius, radius + 1):
            # Half-width at this row: sqrt(r^2 - dy^2)
            half_w = int(math.sqrt(max(0, radius * radius - dy * dy)))
            for dx in range(-half_w, half_w + 1):
                set_pixel(pixels, pitch, cx + dx, cy + dy, color, buf_w, buf_h)
    else:
        # Outline only: midpoint circle algorithm
        x, y = radius, 0
        err = 1 - radius
        while x >= y:
            # Draw 8 symmetric points (circle has 8-fold symmetry)
            for sx, sy in [(x, y), (-x, y), (x, -y), (-x, -y),
                           (y, x), (-y, x), (y, -x), (-y, -x)]:
                set_pixel(pixels, pitch, cx + sx, cy + sy, color, buf_w, buf_h)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1


def draw_line_pixels(pixels, pitch, x0, y0, x1, y1, color, buf_w, buf_h):
    """
    Draw a line using Bresenham's line algorithm.

    The problem: a line between two points passes through continuous space,
    but pixels are discrete. Bresenham's algorithm picks the closest pixel
    at each step using only integer arithmetic (no floats = fast).
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1  # Step direction
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        set_pixel(pixels, pitch, x0, y0, color, buf_w, buf_h)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


# =============================================================================
# STEP 7: Main program
# =============================================================================
def main():
    WIDTH, HEIGHT = 800, 600

    # --- Initialize SDL2 ---
    # This sets up the video driver, connects to the OS windowing system, etc.
    if sdl2.SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) != 0:
        print(f"SDL_Init failed: {sdl2.SDL_GetError()}")
        sys.exit(1)
    print("SDL2 initialized")

    # --- Create a window ---
    # This asks the OS for a window. On Mac, this creates an NSWindow via Cocoa.
    # The window is just a frame — it doesn't have any drawing surface yet.
    window = sdl2.SDL_CreateWindow(
        b"Layer 1: Raw SDL2 Pixels",  # Title (C string = bytes)
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        WIDTH, HEIGHT,
        SDL_WINDOW_SHOWN,
    )
    if not window:
        print(f"SDL_CreateWindow failed: {sdl2.SDL_GetError()}")
        sys.exit(1)
    print(f"Window created: {WIDTH}x{HEIGHT}")

    # --- Create a renderer ---
    # The renderer is the bridge between our code and the GPU. It manages
    # a "back buffer" that we draw to, then flips it to the screen.
    # -1 = use the first available rendering driver (Metal on Mac, D3D on Windows)
    renderer = sdl2.SDL_CreateRenderer(
        window, -1,
        SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC,
    )
    if not renderer:
        print(f"SDL_CreateRenderer failed: {sdl2.SDL_GetError()}")
        sys.exit(1)
    print("Renderer created (hardware-accelerated)")

    # --- Create a streaming texture ---
    # This is our pixel buffer. It lives on the GPU but we can "lock" it to
    # get a CPU-side pointer, write pixel data, then "unlock" to upload.
    # Think of it as a canvas we paint on.
    texture = sdl2.SDL_CreateTexture(
        renderer,
        SDL_PIXELFORMAT_ARGB8888,     # 4 bytes per pixel
        SDL_TEXTUREACCESS_STREAMING,  # We'll write to it every frame
        WIDTH, HEIGHT,
    )
    if not texture:
        print(f"SDL_CreateTexture failed: {sdl2.SDL_GetError()}")
        sys.exit(1)
    print("Streaming texture created (pixel buffer)")

    # --- Event and timing setup ---
    event = SDL_Event()
    running = True
    frame = 0
    space_pressed = False

    print("\nControls:")
    print("  SPACE = toggle animation pause")
    print("  ESC   = quit")
    print("  Close window = quit\n")

    # --- Main loop ---
    # This is THE game loop. Every game engine has one:
    #   1. Poll events (input from OS)
    #   2. Update state (game logic)
    #   3. Render (draw to screen)
    #   4. Present (flip buffer)
    #   5. Wait (frame timing)

    while running:
        frame_start = sdl2.SDL_GetTicks()

        # ----- POLL EVENTS -----
        # SDL collects OS events (key presses, mouse moves, window close, etc.)
        # into an internal queue. We drain it each frame.
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == SDL_QUIT:
                running = False

            elif event.type == SDL_KEYDOWN:
                scancode = event.key.scancode
                if scancode == SDL_SCANCODE_ESCAPE:
                    running = False
                elif scancode == SDL_SCANCODE_SPACE and not event.key.repeat:
                    space_pressed = not space_pressed
                    print(f"Animation {'paused' if space_pressed else 'resumed'}")

        # ----- UPDATE STATE -----
        if not space_pressed:
            frame += 1

        # ----- RENDER: Lock the texture to get a raw pixel pointer -----
        pixel_ptr = ctypes.c_void_p()
        pitch = ctypes.c_int()

        # SDL_LockTexture gives us:
        #   pixel_ptr: pointer to the pixel memory (CPU-accessible)
        #   pitch: bytes per row (may be > width*4 due to GPU alignment)
        if sdl2.SDL_LockTexture(
            texture, None,
            ctypes.byref(pixel_ptr), ctypes.byref(pitch),
        ) != 0:
            print(f"SDL_LockTexture failed: {sdl2.SDL_GetError()}")
            break

        pixels = pixel_ptr.value  # Raw memory address as integer
        p = pitch.value           # Bytes per row

        # ----- CLEAR: Fill every pixel with dark background -----
        bg_color = argb(20, 20, 30)
        for y in range(HEIGHT):
            row = ctypes.cast(
                ctypes.c_void_p(pixels + y * p),
                ctypes.POINTER(ctypes.c_uint32),
            )
            for x in range(WIDTH):
                row[x] = bg_color

        # ----- DRAW: Animated content -----
        t = frame * 0.02  # Time variable for animations

        # 1. Gradient bar at the top — shows how RGB values map to colors
        bar_height = 40
        for y in range(bar_height):
            for x in range(WIDTH):
                r = int(255 * x / WIDTH)
                g = int(255 * (1 - x / WIDTH))
                b = int(128 + 127 * math.sin(t + x * 0.01))
                set_pixel(pixels, p, x, y, argb(r, g, b), WIDTH, HEIGHT)

        # 2. Moving rectangle — bouncing box
        box_size = 60
        box_x = int(WIDTH / 2 + 200 * math.sin(t)) - box_size // 2
        box_y = int(HEIGHT / 2 + 100 * math.cos(t * 1.3)) - box_size // 2
        draw_rect_pixels(
            pixels, p, box_x, box_y, box_size, box_size,
            argb(0, 200, 100), WIDTH, HEIGHT,
        )

        # 3. Outlined rectangle — shows filled vs outline
        draw_rect_pixels(
            pixels, p, box_x - 10, box_y - 10, box_size + 20, box_size + 20,
            argb(200, 200, 0), WIDTH, HEIGHT, filled=False,
        )

        # 4. Orbiting circles
        for i in range(5):
            angle = t + i * (2 * math.pi / 5)
            cx = int(WIDTH / 2 + 150 * math.cos(angle))
            cy = int(HEIGHT / 2 + 150 * math.sin(angle))
            r = int(128 + 127 * math.sin(t + i))
            g = int(128 + 127 * math.sin(t + i + 2))
            b = int(128 + 127 * math.sin(t + i + 4))
            draw_circle_pixels(pixels, p, cx, cy, 20, argb(r, g, b), WIDTH, HEIGHT)

        # 5. Center circle outline
        draw_circle_pixels(
            pixels, p, WIDTH // 2, HEIGHT // 2, 150,
            argb(100, 100, 255), WIDTH, HEIGHT, filled=False,
        )

        # 6. Lines radiating from center — like a starburst
        num_lines = 12
        for i in range(num_lines):
            angle = t * 0.5 + i * (2 * math.pi / num_lines)
            ex = int(WIDTH / 2 + 180 * math.cos(angle))
            ey = int(HEIGHT / 2 + 180 * math.sin(angle))
            r = int(200 + 55 * math.sin(t + i))
            draw_line_pixels(
                pixels, p, WIDTH // 2, HEIGHT // 2, ex, ey,
                argb(r, 100, 150), WIDTH, HEIGHT,
            )

        # ----- UPLOAD: Unlock the texture (sends pixels to GPU) -----
        sdl2.SDL_UnlockTexture(texture)

        # ----- PRESENT: Copy texture to screen and flip -----
        # RenderCopy blits our texture to the renderer's back buffer
        # RenderPresent swaps back buffer to front (what you see)
        sdl2.SDL_RenderCopy(renderer, texture, None, None)
        sdl2.SDL_RenderPresent(renderer)

        # ----- TIMING: Print FPS every 60 frames -----
        if frame % 60 == 0:
            elapsed = sdl2.SDL_GetTicks() - frame_start
            print(f"Frame {frame} | last frame: {elapsed}ms", end="\r")

    # --- Cleanup ---
    # Release everything in reverse order of creation.
    # Forgetting this causes resource leaks (GPU memory, OS handles).
    print("\nShutting down...")
    sdl2.SDL_DestroyTexture(texture)
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()
    print("Done.")


if __name__ == "__main__":
    main()
