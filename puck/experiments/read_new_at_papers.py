import cv2 as cv
from matplotlib import pyplot as plt
import math

DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)

def area_of_frame(frame):
    x0 = frame[0][0]
    x1 = frame[1][0]
    y0 = frame[0][1]
    y1 = frame[1][1]
    return abs(y0-y1)* abs(x0-x1)

def bigger_smaller_frame(frame_0, frame_1):
 if area_of_frame(frame_0)> area_of_frame(frame_1):
    return (frame_0, frame_1)
 else:
    return (frame_1, frame_0)

def frame_to_polygon_list(frame):
    x0 = int(frame[0][0])
    x1 = int(frame[1][0])
    y0 = int(frame[0][1])
    y1 = int(frame[1][1])
    return [(x0,y0), (x0,y1), (x1,y1), (x1,y0)]

def frames(path):
    input = cv.imread(path)
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    ## grab the first two ids and their coordinates, that's all we're considering rn
    corners_a = corners[0][0]
    corners_b = corners[1][0]
    frame_0 = (corners_a[1], corners_b[3])
    frame_1 = (corners_a[3], corners_b[1])
    outer_frame, inner_frame = (bigger_smaller_frame(frame_0, frame_1))
    return (outer_frame, inner_frame, ids)

outer_frame, inner_frame, ids= frames("puck/apriltag_stills/test_0.png")
outer_polygon = frame_to_polygon_list(outer_frame)
inner_polygon = frame_to_polygon_list(inner_frame)
