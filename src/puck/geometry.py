import math

def angle_to(p, q):
    """Angle in radians from p to q, clockwise from horizontal right."""
    if p == q:
        raise ValueError("no angle from a point to itself")
    
    px, py = p
    qx, qy = q

    dx = qx - px
    dy = qy - py

    if dx == 0:
        if dy > 0:
            angle = math.pi /2
        else:
            angle = -math.pi / 2
    else:
        angle = math.atan(dy/dx)

    if dx < 0:
        angle += math.pi

    return angle


def clockwise_pt(points, black):
    """The point that is the one clockwise from black, in the square formed by points."""
    other_corners = [pt for pt in points if pt != black]
    dists_to_corners = [math.dist(black, q) for q in other_corners]
    furthest = max(dists_to_corners)
    opposite_corner = other_corners[dists_to_corners.index(furthest)]

    adjacent_corners = [pt for pt in other_corners if pt != opposite_corner]
    angles_to_corners = [angle_to(black, q) for q in adjacent_corners]

    angle_range = max(angles_to_corners) - min(angles_to_corners)

    if angle_range < math.pi:
        # should be about pi/2
        clockwise_angle = min(angles_to_corners)
    else:
        # should be about 3/2 pi
        clockwise_angle = max(angles_to_corners)

    clockwise_pt = adjacent_corners[angles_to_corners.index(clockwise_angle)]
    return clockwise_pt


def order_no_color_rectangle(point_list, reference):
    ordered = [None, None, None]
    ordered[0] = clockwise_pt(point_list, reference)
    ordered[1] = clockwise_pt(point_list, ordered[0])
    ordered[2] = clockwise_pt(point_list, ordered[1])
    assert ordered[0] != ordered[1]
    assert ordered[1] != ordered[2]
    assert ordered[0] != ordered[2]
    return ordered

