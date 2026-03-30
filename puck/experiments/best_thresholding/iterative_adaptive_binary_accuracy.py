from time import thread_time_ns
import numpy as np
from pathlib import Path
import itertools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import json
import math
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


def runShortPipeline(shortenedImageList, choice, choice_dict, times_dict,file_data, input_path, count_of_images):
    blobcounts=[]
    correct = 0
    close_enough_count =0
    for path in shortenedImageList:
        gtkp = groundTruthKeyPoints(file_data.get("images"+(str(path)[len(input_path):])))
        image = cv.imread(path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 3)
        blob_params = blobParamFunc(400, .8)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        if choice == 0 : # binary
            _, thresholded = cv.threshold(gray, 170, 255, cv.THRESH_BINARY)
            detector = cv.SimpleBlobDetector_create(blob_params)
            keypoints = detector.detect(thresholded)
            point_list = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        elif choice == 1: ## adaptive global -50 
            informed_threshold = gray.max() - 50
            # print(informed_threshold)
            _, thresholded = cv.threshold(gray, informed_threshold , 255, cv.THRESH_BINARY)
            detector = cv.SimpleBlobDetector_create(blob_params)
            keypoints = detector.detect(thresholded)
            point_list = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        elif choice == 2:
            informed_threshold = gray.max() - 20
            # print(informed_threshold)
            _, thresholded = cv.threshold(gray, informed_threshold , 255, cv.THRESH_BINARY)
            detector = cv.SimpleBlobDetector_create(blob_params)
            keypoints = detector.detect(thresholded)
            point_list = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        elif choice == 3:
            informed_threshold = gray.max() - 80
            # print(informed_threshold)
            _, thresholded = cv.threshold(gray, informed_threshold , 255, cv.THRESH_BINARY)
            detector = cv.SimpleBlobDetector_create(blob_params)
            keypoints = detector.detect(thresholded)
            point_list = [(round(kp.pt[0]), round(kp.pt[1])) for kp in keypoints]
        elif choice == 4:
            ## iterative-2
            thresholds = np.arange(160,180,10)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
        elif choice == 5:
             ## iterative-5
            thresholds = np.arange(150,200,10)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
        elif choice == 6:
             ## iterative-10
            thresholds = np.arange(100,200,10)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
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
        if close_enough:
            close_enough_count +=1
        if only_4_close_enough:
            correct += 1
        blobcounts.append(count_of_blobs)
    choice_human = choice_dict.get(str(choice))
    #f"{choice_human}_blobcounts": blobcounts,
    times_dict.update({ f"{choice_human}_correct_acc": correct/count_of_images, f"{choice_human}_close4_acc": close_enough_count/count_of_images})


def main(input_path = "data/images_miniset",ground_truth = "data/annotations/annotations.json", output_folder= "output/experimental_results/" , output_name = "iterative_adaptive_binary", cli_output=True):
        
    with open(ground_truth , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))
    
    p = Path('.')

    imageList = [path for path in sorted(list(p.glob(f'{input_path}/*/*/*/*/*0.jpg')))]
    choice_dict = {"0": "binary", "1": "adaptive_global-50", "2": "adaptive_global-20", "3": "adaptive_global-80",  "4": "iterative-2","5": "iterative-5", "6": "iterative-10",}

    times_dict ={}
    for choice in tqdm(range(0,7,1)):
        runShortPipeline(imageList, choice, choice_dict, times_dict,file_data, input_path, len(imageList))

    with open(f'{output_folder}{output_name}.json', 'w') as f:
        json.dump(times_dict, f)
    if cli_output:
        print(f"This experiment used the {input_path} and created{output_name}.json in {output_folder}.")
    return f'{output_folder}{output_name}.json'
##This has tested 3 iterative thresholding approaches, 3 adaptive global thresholding approaches and one binary threshold for a baseline. \n \
##It tests the adaptive global at maximum - c where c is 20, 50, and 80. It tests the iterative with 2,5, and 10 thresholds. The binary threshold is 170


if __name__ == "__main__":
    main()