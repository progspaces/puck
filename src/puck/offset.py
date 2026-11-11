from screeninfo import get_monitors

def offset_string():
    monitors = get_monitors()
    if len(monitors) == 1:
        raise Exception("You do not seem to have a secondary monitor plugged "
        "in. Please remedy this.")
    for m in monitors:
        if not m.is_primary:
            return f"{m.width}x{m.height}+{m.x}+-{m.y}"

def size_of_second():
    monitors = get_monitors()
    if len(monitors) == 1:
        raise Exception("You do not seem to have a secondary monitor plugged "
        "in. Please remedy this.")
    for m in monitors:
        if not m.is_primary:
            return m.height, m.width

