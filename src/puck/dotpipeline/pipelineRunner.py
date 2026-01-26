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

def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]

def pipelineTests(args):
    test_pipeline, choice = args
    results_path = Path("src/puck/dotpipeline/pipeline_results/" + str(choice))
    results_path.mkdir(parents=True, exist_ok=True)
    # print(test_pipeline)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        start = thread_time_ns()
    # for x in range(1,2,1):
        # img_path = "images/custom/davids/short/B/custom_davids_short_B_0.jpg"
        gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, test_pipeline[0])
        thresholded1 = False
        thresholded2 = False
        if choice == 0 : # binary
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            _, thresholded = cv.threshold(gray, test_pipeline[3], 255, cv.THRESH_BINARY)
        elif choice == 1: ## Adaptive Mean
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            thresholded1 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,test_pipeline[3],test_pipeline[4])
            thresholded2 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,test_pipeline[3],test_pipeline[4])
        elif choice == 2: ## Adaptive Gaussian
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            thresholded1 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,test_pipeline[3],test_pipeline[4])
            thresholded2 = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,test_pipeline[3],test_pipeline[4])
        else: 
            # convert the image into the hsv colour space
            image_hsv = cv.cvtColor(imageBlurred, cv.COLOR_RGB2HSV)
            image_hsv = imageBlurred
    
            # use Otsu's method to find the thresholds for hue and saturation
            _, thresh_v = cv.threshold(image_hsv[:, :, 2],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    
            # mask the image to get determine which pixels with hue and saturation above their thresholds
            mask_v= image_hsv[:, :, 1] > thresh_v
    
            # combine the masks with an OR so any pixel above either threshold counts as foreground
    
            # apply morphological transforms
            kernel = np.ones((3, 3), np.uint8)
            thresholded = cv.morphologyEx(mask_v.astype(np.uint8), cv.MORPH_CLOSE, kernel)
            thresholded= thresholded*255
            # # print(thresholded)
            thresholded = 255-thresholded
            
        blob_params = blobParamFunc(test_pipeline[1], test_pipeline[2])
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
pipelines = ["src/puck/dotpipeline/binary0.json","src/puck/dotpipeline/adaptiveM0.json","src/puck/dotpipeline/adaptiveG0.json", "src/puck/dotpipeline/otsu0.json"]

# Manually set this, (choice choice_time), so 0-3, and then 0 initially for choice_time, reset at the end of each for loop.
choices = [(0,0),(3,0)]
p = Path('.')


for choice, choice_time in choices:
    choice_start = thread_time_ns()
    pipeline_list_dict = {}
    with ThreadPoolExecutor(10) as pool:
        # call a function on each item in a list and handle results
        generatored_pipelines = generator(pipelines[choice])[1]
        list_of_choices = [choice] * len(generatored_pipelines)

        for name, result in tqdm(pool.map(pipelineTests, zip(generatored_pipelines, list_of_choices)), total=len(generatored_pipelines)):
            pipeline_list_dict.update({name:result})

    # ensure that output directory exists for the big picture
    output_dir = Path("src/puck/dotpipeline/big_picture/")        
    output_dir.mkdir(parents=True, exist_ok=True)

    # save the big picture results
    pd.DataFrame(pipeline_list_dict).T.to_csv(output_dir / (str(pipelines[choice])[21:]+ "_results.csv"))
    choice_time = thread_time_ns() - choice_start
    

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
    
   