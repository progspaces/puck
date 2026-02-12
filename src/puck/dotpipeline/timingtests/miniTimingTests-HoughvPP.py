from time import thread_time_ns
import numpy as np
from pathlib import Path
import random
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
import sys
from puck.dotpipeline.timingtests.Computation_time_reporter import TimeOutput

with open('./src/puck/datacollection/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]

def detection(thresholds,blob_params, gray):
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




def pipeline(imgList, choice, times_dict, times_dict_sum):
    times = []
    all_start = thread_time_ns()
    correct = 0
    for path in imgList:
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get((str(path)[:])))
        image = cv.imread(path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 3)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        if choice == 0: ## paper programs
            # print("paper programs")
            thresholds = np.arange(160,190,10)
            blob_params = blobParamFunc(400, .8)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
        else: ## hough
            # print("hough")
            rows = gray.shape[0]
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                        param1=100, param2=30,
                        minRadius=10, maxRadius=30)[:,:,0:2][0]
            point_list = [(float(c[0]),float(c[1])) for c in circles]
        end = thread_time_ns()
        print(str(path) , str((end-start)/1_000_000_000))


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
    times_dict_sum.update({f"{choice}_all_time": all_time,f"{choice}_avg": avgTimeToDetect, f"{choice}_median": medianTimeToDetect, f"{choice}_correct": correct})
    times_dict.update({f"{choice}_times": times})

overall_start = thread_time_ns()
random.seed(2026)
p = Path('.')

imageList = [path for path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg')))]

times_dict ={}
times_dict_sum ={}
for choice in tqdm(range(0,2,1)):
    pipeline(imageList, choice, times_dict,times_dict_sum )
    print(times_dict_sum)

with open('./results/timingDict_hvpp_summary.json', 'w') as f:
    json.dump(times_dict_sum, f)

with open('./results/timingDict_hvpp_raw.json', 'w') as f:
    json.dump(times_dict, f)

total_time = thread_time_ns() - overall_start
file_out = open(f'./results/timingDict_hvpp_computation_time_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"', 'w')
sys.stdout = file_out
TimeOutput(total=total_time)
file_out.close()






