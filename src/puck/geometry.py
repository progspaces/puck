import math

def angle_to(p, q):
    """Get the angle from p to q in radians from horizontal right.

    Args:
        p (tuple[int,int]): starting point
        q (tuple[int,int]): ending point

    Raises:
        ValueError: There is no angle to return if the points are identical.

    Returns:
        int: angle in radians from p to q clockwise from horizontal right.
    """
    if p == q:
        raise ValueError("no angle from a point to itself")

    # Decompose points into their x and y components
    px, py = p 
    qx, qy = q

    # Find the dx and dy between the points.
    dx = qx - px
    dy = qy - py

    # if dx is 0, then we are looking at an angle of pi/2 
    # depending on if the ending point is above or below the starting point.
    # If one imagines a clock, this is the angle from 3:00 to 12:00 or to 6:00.
    if dx == 0:
        if dy > 0:
            angle = math.pi / 2
        else:
            angle = -math.pi / 2
    # Otherwise one can use the arctan of the slope to find all other possible angles.
    else:
        angle = math.atan(dy / dx)

    # If the dx is negative, 
    # you must add a pi to the radian calculation get the right result.
    if dx < 0:
        angle += math.pi

    return angle


def clockwise_pt(points, reference):
    """
    Gets you the point that is the next clockwise point from reference point, 
    in a rectangle formed by four points.

    Args:
        points list[tuple[int,int]]: All the points in the rectangle other than the reference point
        reference tuple[int,int]: The point that you're using to decide where to go next from.

    Returns:
        tuple[int, int]: Clockwise point in rectangle from given reference.
    """
    other_corners = [pt for pt in points if pt != reference] # get rid of the refernce point
    dists_to_corners = [math.dist(reference, q) for q in other_corners] # find out how far away every other point is from the reference 
    furthest = max(dists_to_corners) # find out the furthest point from the point you have (ought to be the diagonal)
    opposite_corner = other_corners[dists_to_corners.index(furthest)]

    adjacent_corners = [pt for pt in other_corners if pt != opposite_corner]
    angles_to_corners = [angle_to(reference, q) for q in adjacent_corners]

    angle_range = max(angles_to_corners) - min(angles_to_corners)

    if angle_range < math.pi:
        # should be about pi/2
        clockwise_angle = min(angles_to_corners)
    else:
        # should be about 3/2 pi
        clockwise_angle = max(angles_to_corners)

    clockwise_pt = adjacent_corners[angles_to_corners.index(clockwise_angle)]
    return clockwise_pt


def ordered_rectangle(point_list, reference):
    """ Orders a list of points that make up a rectangle by going clockwise through them, 
    starting with the given reference point.

    Args:
        point_list list[tuple[int,int]]: A list of four points.
        reference tuple[int,int]: The starting point to order the rectangle from.
    Returns:
        list[tuple[int,int]]: A list of four points ordered clockwise from the reference point.
    """
    ordered = []
    # Walk clockwise through the ordered list.
    ordered.insert(0, clockwise_pt(point_list, reference))
    ordered.insert(1,clockwise_pt(point_list, ordered[0]))
    ordered.insert(2,clockwise_pt(point_list, ordered[1]))
    ordered.insert(0, reference)
    ## Double check we haven't assigned the same point multiple times.....
    assert len(set(ordered)) == 4
    return ordered
