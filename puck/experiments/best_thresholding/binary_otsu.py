import itertools
from concurrent.futures import ThreadPoolExecutor
from puck.experiments.best_thresholding.cartesian_product import generator
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


def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]

def pipelineTests(args):
    test_pipeline = args
    results_path = Path("src/puck/dotpipeline/pipeline_results/" + str(choice))
    results_path.mkdir(parents=True, exist_ok=True)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        # print(str(img_path))
        gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
        start= thread_time_ns()
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 9)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        thresholds = [160,170,180]
        blob_params = blobParamFunc(500, .8)
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
        if only_4_close_enough:
            correct += 1
        timeToDetect = end - start
        times.append(timeToDetect)
        pipeline_img_dict.update({img_path: (count_of_blobs, close_enough, only_4_close_enough, timeToDetect,distances)})
        # # print("...")
    # Create subdirectory for choice results
    choice_results_path = results_path / str(choice)
    choice_results_path.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(pipeline_img_dict).T.to_csv(choice_results_path / (str(test_pipeline) + "_results.csv"))
    accuracy = (correct/480)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    return str(test_pipeline), (choice, accuracy, avgTimeToDetect, medianTimeToDetect)




overall_start = thread_time_ns()

# Open the ground truth annotations
with open('./src/puck/cli/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

# Get the pipeline configuration options

# Manually set this, (choice choice_time), so 0-3, and then 0 initially for choice_time, reset at the end of each for loop.
choices = [("paperPrograms",0)]
p = Path('.')


for choice, choice_time in choices:
    choice_start = thread_time_ns()
    pipeline_list_dict = {}
    with ThreadPoolExecutor(10) as pool:
        # call a function on each item in a list and handle results
        generatored_pipelines = generator("/Users/jdreiling/Desktop/puck/puck/src/puck/dotpipeline/binary1.json")[1]
        for name, result in tqdm(pool.map(pipelineTests, generatored_pipelines), total=len(generatored_pipelines)):
            pipeline_list_dict.update({name:result})

    # ensure that output directory exists for the big picture
    output_dir = Path("src/puck/dotpipeline/big_picture/")        
    output_dir.mkdir(parents=True, exist_ok=True)

    # save the big picture results
    pd.DataFrame(pipeline_list_dict).T.to_csv(output_dir / "paperProgramsThresholding_results.csv")
    choice_end =thread_time_ns()
    choice_time = choice_end - choice_start
    

overall_end = thread_time_ns()
overall_time = overall_end - overall_start

txtStr = f"This pipeline runner took {overall_time} time in total. \n" 
for option, option_time in choices:
    txtStr = txtStr + f"It spent {option_time} time on choice {option}. \n"

# Ensure timing results directory exists
timing_dir = Path('./src/puck/dotpipeline/')
timing_dir.mkdir(parents=True, exist_ok=True)

# Create timing results file with properly formatted datetime
timing_filename = timing_dir / f"timingResults_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(timing_filename, "w") as txt_file:
    txt_file.write(txtStr)
    
   