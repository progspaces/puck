import itertools
from concurrent.futures import ThreadPoolExecutor
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

def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]


def detection(thresholds,blob_params,gray):
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
                    distance = math.dist(curr_center, c)
                    isNew = distance >= 10
                    if not isNew:
                        break
            if isNew:
                new_centers.append(curr_center)
        centers = centers + new_centers
    return centers


def main(input = "data/images_miniset", output_timing = "./output/timing_results", output_experimental = "./output/experimental_results",ground_truth='./data/annotations/annotations.json', cli_printout = True):
# Open the ground truth annotations
    with open(ground_truth , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))

    # Get the pipeline configuration options

    p = Path('.')

    # test on 96 images, 20% of the images possible
    # one binary
    # two binary
    # three binary
    # four binary
    # five binary
    # 10 binary
    # 15 binary
    thresh_dict = {
        0: [170],#1
        1: [170,180], #2
        2: [160,170,180], #3
        3: np.arange(150,190,10), #4
        4: np.arange(150,200,10), #5
        5: np.arange(100,200,10), #10
        6: np.arange(50,250,10),
    }
    results = {}
    time_dict = {
        0: [],#1
        1: [], #2
        2: [], #3
        3: [],
        4: [],
        5: [],
        6: [],
    }
    for img_path in tqdm(sorted(list(p.glob(f'{input}/*/*/*/*/*0.jpg')))):
        truthPath = ("images" + str(img_path)[len(input):])
        gtkp = groundTruthKeyPoints(file_data.get(str(truthPath)))
        # print(truthPath) 
        for x in range(0,7,1):
            start= thread_time_ns()
            image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
            imageBlurred = cv.medianBlur(image, 3)
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            thresholds = thresh_dict.get(x)
            # print(thresholds) 
            blob_params = blobParamFunc(300, .75)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
            end = thread_time_ns() 
            distances = []
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
            # variable list
            count_of_blobs = len(point_list)
            only_4 = len(point_list) == 4
            close_enough = True if all([(dist < 5) for dist in first_four]) else False
            only_4_close_enough = only_4 and close_enough
            timeToDetect = (end - start)
            count_thresh = len(thresholds)
            list_times = time_dict.get(x)
            list_times.append(timeToDetect)
            time_dict.update({x:list_times})
            results.update({str(img_path)+ "."+str(len(thresholds)):(len(thresholds),count_of_blobs, close_enough, only_4_close_enough, timeToDetect,distances)})

    with open(f'{output_experimental}/iterative_dict.json', 'w') as f:
        json.dump(results, f)

    with open(f'{output_timing}/timing_iterative_dict.json', 'w') as f:
        json.dump(time_dict, f)
    if cli_printout:
        print(f"This is a timing test run on {input}, for the iterative paper programs thresholding method.\n\
This tests 1, 2, 3, 4, 5, 10, and 15 possible thresholds. \n \
This will save two .json files at {output_experimental} and {output_timing}. \n\
They are {output_experimental}/iterative_dict.json and {output_timing}/timing_iterative_dict.json.\n\
The {output_experimental}/iterative_dict.json just returns how accurate the threshold was, whereas \
{output_timing}/timing_iterative_dict.json records how long the thresholds took.")

if __name__ == "__main__":
    main()
