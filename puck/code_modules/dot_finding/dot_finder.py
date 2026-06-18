import cv2 as cv
from math import dist
import numpy as np
import matplotlib.pyplot as plt

def find_centers_hough(file_path, min_dist, grayscale = False, minRadius=15, maxRadius=30,image_colorsaved = "RGB"):
    '''
    CALIBRATION_MIN_DIST = 30
    PROGRAM_MIN_DIST = 170
    '''
    image = cv.imread(file_path, cv.IMREAD_COLOR_RGB)
    imageBlurred = cv.medianBlur(image, 3)
    gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT_ALT,1.5, min_dist, param1=300, param2=.9, minRadius=minRadius, maxRadius=maxRadius)
    if grayscale == True:
        image_copy = image.copy()
        image_copy_grey = gray.copy()
        # image_copy = cv.cvtColor(image_copy, cv.COLOR_RGB2BGR)
        if circles is not None:
            circles2 = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles2:
		# draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
                cv.circle(image_copy, (x, y), r, (0, 255, 0), 4)
                cv.circle(image_copy_grey, (x, y), r, (0, 255, 0), 4)
                # print(f"x is {x}, y is {y}, r is {r}")
                cv.rectangle(image_copy, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                cv.rectangle(image_copy_grey, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            cv.imshow("markedup output", image_copy)
            cv.imshow("markedup grey", image_copy_grey)
            cv.waitKey(0)
    circles = circles[:,:,0:2][0] if circles is not None else []
    point_list = [(int(c[0]),int(c[1])) for c in circles]
    # print(point_list)
    return (point_list, cv.imread(file_path, cv.IMREAD_COLOR_BGR)) if image_colorsaved == "BGR" else (point_list, image)


def find_centers_hough_frames(frame, min_dist, grayscale = True,minRadius=15, maxRadius=30):
    '''
    CALIBRATION_MIN_DIST = 30
    PROGRAM_MIN_DIST = 170
    '''
    image = frame
    imageBlurred = cv.medianBlur(image, 3)
    gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT_ALT,1.5, min_dist, param1=300, param2=.9, minRadius=minRadius, maxRadius=maxRadius)
    if grayscale == True:
        if circles is not None:
            circles2 = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles2:
		# draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
                cv.circle(gray, (x, y), r, (0, 255, 0), 4)
                print(f"x is {x}, y is {y}, r is {r}")
                cv.rectangle(gray, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            cv.imshow("output", np.hstack([gray, gray]))
            cv.waitKey(0)
    circles = circles[:,:,0:2][0] if circles is not None else []
    point_list = [(int(c[0]),int(c[1])) for c in circles]
    return (point_list,image)


def stepwise_detection(thresholds,blob_params, gray):
    detector = cv.SimpleBlobDetector_create(blob_params)
    centers= []
    for thresh in thresholds:
        _, thresholded = cv.threshold(gray, thresh, 255, cv.THRESH_BINARY)
        keypoints = detector.detect(thresholded)
        current_centers = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        new_centers = []
        for curr_center in current_centers:
            isNew = True
            for c in centers:
                    distance = dist(curr_center, c)
                    isNew = distance >= 10
                    if not isNew:
                        break
            if isNew:
                new_centers.append(curr_center)
        centers = centers + new_centers
    return centers


def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def find_centers_mthresh(file_path):
    image = cv.imread(file_path, cv.IMREAD_COLOR_RGB)
    imageBlurred = cv.medianBlur(image, 3)
    gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
    thresholds = np.arange(150,200,10)
    blob_params = blobParamFunc(400, .8)
    point_list = stepwise_detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
    return (point_list,image)
     

