from time import thread_time_ns
import numpy as np
from pathlib import Path
import random
import itertools
from concurrent.futures import ThreadPoolExecutor
# from hypersearch.pipelineGenerator import generator
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
    # print(entry)  
    return [tuple(point[1:3]) for point in entry]


def runShortPipeline(shortenedImageList, input, choice, file_data, choice_dict,timesDict):
    times = []
    blobcounts=[]
    all_start = thread_time_ns()
    correct = 0
    close_enough_count =0
    for path in shortenedImageList:
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get("images"+(str(path)[len(input):])))
        image = cv.imread(path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 3)
        if choice == 0 : # binary
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            _, thresholded = cv.threshold(gray, 170, 255, cv.THRESH_BINARY)
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
        if close_enough:
            close_enough_count +=1
        if only_4_close_enough:
            correct += 1
        timeToDetect = (end - start)
        times.append(timeToDetect)
        blobcounts.append(count_of_blobs)
    all_time = (thread_time_ns() - all_start)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    choice_human = choice_dict.get(str(choice))
    timesDict.update({f"{choice_human}_all_time": all_time, f"{choice_human}_blobcounts": blobcounts, f"{choice_human}_times": times, f"{choice_human}_avg": avgTimeToDetect, f"{choice_human}_median": medianTimeToDetect, f"{choice_human}_correct": correct, f"{choice_human}_close4": close_enough_count})

def main(input:str ="data/images_miniset" , output:str = "./output/timing_results/binary_otsu_adaptive_timing_dict.json", ground_truth_path:str = "./data/annotations/annotations.json", cli_printout:bool= True):
    with open(ground_truth_path , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))
    p = Path('.')
    imageList = [path for path in sorted(list(p.glob(f'{input}/*/*/*/*/*[0-4].jpg')))]
    choice_dict = {"0": "binary", "1": "adaptive_mean", "2": "adaptive_gaussian", "3":"otsu"}
    timesDict ={}
    for choice in tqdm(range(0,4,1)):
        runShortPipeline(imageList, input, choice, file_data, choice_dict, timesDict)
    with open(output, 'w') as f:
        json.dump(timesDict, f)
    if cli_printout:
        print(f"This is a timing test run on {input}. \n \
The timing information has been saved as a .json file at {output} \n \
it has the average time and median time it took to run each of the following possible thresholding method: \n \
          - 0: binary \n \
          - 1: adaptive mean \n \
          - 2: adaptive gaussian \n \
          - 3: otsu \n \
As well as the total time for each, and the time it took per individual image within the {input}.")


if __name__ == "__main__":
    main(cli_printout =True)