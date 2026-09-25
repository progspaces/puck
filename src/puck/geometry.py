import math
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    def __iter__(self):
        return iter((self.x, self.y))

    def __hash__(self):
        return hash((self.x,self.y))

    def dist_to(self:Point, other:Point) -> float:
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        return math.sqrt(dy**2 + dx**2)

    
@dataclass
class Polygon:
    points: list[Point]
    def __getitem__(self, key):
        return self.points[key]

    def __iter__(self):
        return iter(self.points)

    def unwrap(self) -> list[tuple[int,int]]:
        return [(x,y) for x,y in self.points]

    @classmethod
    def from_array(cls, array):
        points = [Point(int(item[0]), int(item[1])) for item in array]
        return cls(points)
    



def angle_to(p: Point, q: Point) -> float:
    """Get the angle in radians from p to q from horizontal right.
    Raises:
        ValueError: There is no angle to return if the points are identical.
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


def clockwise_pt(rectangle: Polygon, reference: Point) -> Point:
    """Gets you the point that is the next clockwise point from reference point, 
    in a rectangle formed by four points.
    """
    other_corners = [pt for pt in rectangle if pt != reference] # get rid of the refernce point
    dists_to_corners = [reference.dist_to(q) for q in other_corners] # find out how far away every other point is from the reference 
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


def ordered_rectangle(rectangle: Polygon, reference: Point) -> Polygon:
    """Orders the points that make up a rectangle by going clockwise through them, 
    starting with the given reference point.
    """
    ordered = []
    # Walk clockwise through the ordered list.
    ordered.insert(0, clockwise_pt(rectangle, reference))
    ordered.insert(1,clockwise_pt(rectangle, ordered[0]))
    ordered.insert(2,clockwise_pt(rectangle, ordered[1]))
    ordered.insert(0, reference)
    ## Double check we haven't assigned the same point multiple times.....
    assert len(set(ordered)) == 4
    return Polygon(ordered)
