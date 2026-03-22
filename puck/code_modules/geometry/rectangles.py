from dataclasses import dataclass
from itertools import combinations
from collections import defaultdict
from math import hypot
import cv2 as cv
import matplotlib.pyplot as plt

@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

    @classmethod
    def from_tuple(cls, coords):
        return cls(coords[0], coords[1])

    def as_tuple(self):
        return (self.x, self.y)


def bucket(value: float, size: float):
    # print(value, int(value / size))
    return int(value / size)

def euc_dist(a: Point, b: Point) -> float:
    return hypot(b.x - a.x, b.y - a.y)

def same_midpoint(pairA, pairB, threshold=20):
    # note - threshold is in pixels
    def midpoint(pair):
        a, b = pair
        return Point((b.x - a.x) / 2.0, (b.y - a.y) / 2.0)

    # compute the midpoints of each pair
    midA = midpoint(pairA)
    midB = midpoint(pairB)

    # are they the same? or rather are they some delta distant
    distance = euc_dist(midA, midB)

    return distance < threshold


def point_as_ints(point):
    return int(point[0]), int(point[1])

def convertRectToList(rect):
    p0, p1, p2, p3 = rect
    p0, p2, p1, p3 = p0.as_tuple(), p2.as_tuple(), p1.as_tuple(), p3.as_tuple()
    return [point_as_ints(p) for p in [p0, p2, p1, p3]]


def get_all_rects(point_list):
    pointified = [Point.from_tuple(pt) for pt in point_list]
    pairs = list(combinations(pointified, 2))
    bucketed = [bucket(round(euc_dist(a, b)), 100) for a, b in pairs]
    tally = defaultdict(list)
    for pair, dist in zip(pairs, bucketed):
        tally[dist].append(pair)
    same_distance_pairs = dict(((dist, pairs) for dist, pairs in tally.items() if len(pairs) > 1))
    all_rects = []
    for _, pairs in same_distance_pairs.items():
        pairs_of_pairs = combinations(pairs, 2)
        rects = [(p1, p2) for (p1, p2) in pairs_of_pairs if same_midpoint(p1, p2)]
        all_rects.extend(rects)
    return all_rects



def displayFoundRect(rect, image):
    out = image.copy()
    p0,p1,p2,p3 = convertRectToList(rect)

    cv.line(out, p0, p2, (255, 0, 0), 10)
    cv.line(out, p0, p1, (255, 0, 0), 10)
    cv.line(out, p3, p1, (255, 0, 0), 10)
    cv.line(out, p3, p2, (255, 0, 0), 10)

    plt.imshow(out)
    plt.show()

def check_rects(point_list):
    all_rects = get_all_rects(point_list)
    checked = []
    for rect in all_rects:
        p0, p2 = rect[0]
        p1, p3 = rect[1]
        rect_point_list = [p0, p2, p1, p3]
        target = Point(0,0)
        rect_point_list.sort(key= lambda p: euc_dist(p, target))
        if rect_point_list not in checked:
            checked.append(rect_point_list)
    return checked