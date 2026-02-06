from time import thread_time_ns
import numpy as np
from pathlib import Path
import random
import itertools
from concurrent.futures import ThreadPoolExecutor
from pipelineGenerator import generator
from pathlib import Path
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import json
import math
import pprint
import pandas as pd
from time import thread_time_ns
from datetime import datetime
import statistics
from tqdm import tqdm

with open('./src/puck/cli/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))
    # print(file_data)

def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]


def runShortPipeline(shortenedImageList, choice, timesDict):
    times = []
    all_start = thread_time_ns()
    correct = 0
    for path in shortenedImageList:
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get("images"+(str(path)[14:])))
        image = cv.imread(path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 3)
        if choice == 0 : # binary
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            _, thresholded = cv.threshold(gray, 3, 255, cv.THRESH_BINARY)
        elif choice == 1: ## Adaptive Mean
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            thresholded1 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,5,2)
            thresholded2 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,5,2)
        elif choice == 2: ## Adaptive Gaussian
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            thresholded1 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,5,2)
            thresholded2 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,5,2)
        else: 
            # convert the image into the hsv colour space
            image_hsv = cv.cvtColor(imageBlurred, cv.COLOR_RGB2HSV)
            image_hsv = imageBlurred
    
            # use Otsu's method to find the thresholds for hue and saturation
            _, thresh_h = cv.threshold(image_hsv[:, :, 0],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
            _, thresh_s = cv.threshold(image_hsv[:, :, 1],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    
            # mask the image to get determine which pixels with hue and saturation above their thresholds
            mask_h = image_hsv[:, :, 1] > thresh_h
            mask_s = image_hsv[:, :, 1] > thresh_s
    
            # combine the masks with an OR so any pixel above either threshold counts as foreground
            np_mask = np.logical_or(mask_h, mask_s)
    
            # apply morphological transforms
            kernel = np.ones((3, 3), np.uint8)
            thresholded = cv.morphologyEx(np_mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
            thresholded= thresholded*255
            # # print(thresholded)
            thresholded = 255-thresholded
            
        blob_params = blobParamFunc(300, .75)
        detector = cv.SimpleBlobDetector_create(blob_params)
        if choice == 1 or choice == 2:
            keypoints1 = detector.detect(thresholded1)
            keypoints2 = detector.detect(thresholded2)
            keypoints = keypoints1 + keypoints2
        else:
            keypoints = detector.detect(thresholded)
        end = thread_time_ns()
        # # print(str(len(keypoints)) + " blobs detected")
        blank = np.zeros((1, 1))
        blobs = cv.drawKeypoints(image, keypoints, blank, (255, 0, 0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        distances = []

        point_list = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        points_to_purge= []
        for a, b in itertools.combinations(point_list, 2):
            dist = (math.dist(a, b))
            if dist<=3:
                points_to_purge.append(a)
        point_list = list(set(point_list) - set(points_to_purge))

        for point in point_list:
            closest = (100000, (0,0))
            for gt in gtkp:
                distance = math.dist(gt, point)
                if distance < closest[0]:
                    closest= (distance, gt,point)
            distances.append(closest[0])
        distances.sort()
        first_four = distances[:4] if len(distances) >= 4 else distances
        count_of_blobs = len(point_list)
        only_4 = len(point_list) == 4
        close_enough = True if all([(dist < 5) for dist in first_four]) else False
        only_4_close_enough = only_4 and close_enough
        if only_4_close_enough:
            correct += 1
        timeToDetect = (end - start)/1000000
        times.append(timeToDetect)
    all_time = (thread_time_ns() - all_start)/1000000
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    timesDict.update({f"{choice}_all_time": all_time, f"{choice}_times": times, f"{choice}_avg": avgTimeToDetect, f"{choice}_median": medianTimeToDetect, f"{choice}_correct": correct})

random.seed(2026)
p = Path('.')

# imageList = [path for path in sorted(list(p.glob('images_miniset/*/*/*/*/*.jpg')))]
# shortenedImageList = [imageList[ind] for ind in random.sample(range(0,95),k=10)]

# timesDict ={}
# for choice in tqdm(range(0,4,1)):
#     runShortPipeline(shortenedImageList, choice, timesDict)
#     print(timesDict)

# with open('timingDict.json', 'w') as f:
#     json.dump(timesDict, f)


with open('./src/puck/dotpipeline/timingDict.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

pprint.pprint(file_data)





