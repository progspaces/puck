import screeninfo


def secondary_monitor() -> screeninfo.Monitor:
    for m in screeninfo.get_monitors():
        if not m.is_primary:
            return m
    raise RuntimeError("No secondary monitor plugged in")


def offset_string() -> str:
    m = secondary_monitor()
    return f"{m.width}x{m.height}+{m.x}+-{m.y}"


def size_of_second() -> tuple[int, int]:
    m = secondary_monitor()
    return m.height, m.width
