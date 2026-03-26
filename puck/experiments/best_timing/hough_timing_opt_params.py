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
from puck.code_modules.helper_functions.computation_time_reporter import TimeOutput


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




def pipeline(imgList, input, choice, times_dict, times_dict_sum,file_data):
    times = []
    all_start = thread_time_ns()
    correct = 0
    for path in imgList:
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get("images"+str(path)[len(input):]))
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
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT_ALT, 1.5, 170,
                        param1=300, param2=.9,
                        minRadius=15, maxRadius=30)[:,:,0:2][0]
            # circles = circles[:,:,0:2][0] if circles is not None else []
            point_list = [(float(c[0]),float(c[1])) for c in circles]
        end = thread_time_ns()
        # print(str(path) , str((end-start)/1_000_000_000))


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

def main(input = "data/images_copy", output_folder ="./output/timing_results/" , output_name ="hough_timing_opt", ground_truth_path = './data/annotations/annotations.json', cli_printout =True):
    with open( ground_truth_path, "r") as json_file:
        file_data = dict(json.loads(json_file.read()))
    overall_start = thread_time_ns()
    p = Path('.')

    imageList = [path for path in sorted(list(p.glob(f'{input}/*/*/*/*/*[0-4].jpg')))]

    times_dict ={}
    times_dict_sum ={}
    for choice in tqdm(range(0,2,1)):
        pipeline(imageList, input, choice, times_dict,times_dict_sum,file_data )
    output_combo = output_folder+output_name
    with open(f'{output_combo}_summary.json', 'w') as f:
        json.dump(times_dict_sum, f)

    with open(f'{output_combo}_raw.json', 'w') as f:
        json.dump(times_dict, f)

    total_time = thread_time_ns() - overall_start
    file_out = open(f'{output_combo}_computation_time_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"', 'w')
    sys.stdout = file_out
    TimeOutput(total=total_time)
    file_out.close()
    sys.stdout = sys.__stdout__
    if cli_printout:
        print(f"This is a timing test run on {input}, for the optimal hough parameters.\n\
This will save two .json files, and one .txt file at {output_folder}. \n\
They are {output_name}_summary.json, {output_name}_raw.json, and {output_name}_computational_time_text_[datetime].txt.\n\
The summary will give you the average and median per image for that config as well as total times for all the images and \
the overall correct, where correct is finding exactly 4 dots and they are all within a tolerance of 5 pixels of the ground truth.\n\
The raw json will give you each time for each image.\n\
The computational time txt file is generated by the computational_time_reporter.py program written by David Harris-Birtill \
and is included for repeatability purposes.")


if __name__ == "__main__":
    main()

