import itertools
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

## A file to check the hyper parameters of CV as well as compare the houghCircle function in OpenCV to the scikit-image hough_ellipse function.
## Use hyper paremter files, houghCircle.json for cv and houghEllispe.json for scikit


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

def pipelineTests(args):
    p = Path('.')
    choice, input_path, file_data, results_path = args
    results_path = Path(f"{results_path}")
    results_path.mkdir(parents=True, exist_ok=True)
    # print(test_pipeline)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob(f'{input_path}/*/*/*/*/*[0-4].jpg'))):
        start = thread_time_ns()
        adjusted_path = ("images"+ str(img_path)[len(input_path):])
        # print(adjusted_path)
        # print(img_path)
        gtkp = groundTruthKeyPoints(file_data.get("images"+ str(img_path)[len(input_path):]))
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        # print(image)
        imageBlurred = cv.medianBlur(image, 3)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        if choice == "houghCircle":
            rows = gray.shape[0]
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                               param1=100, param2=30,
                               minRadius=1, maxRadius=30)
            circles = circles[:,:,0:2][0] if circles is not None else []
            point_list = [(float(c[0]),float(c[1])) for c in circles]
        else:
            thresholds = np.arange(160,190,10)
            blob_params = blobParamFunc(400, .8)
            point_list = detection(thresholds=thresholds, blob_params= blob_params, gray=gray)
        end = thread_time_ns()
        # print(test_pipeline, str(img_path)[:-4] , str((end-start)/1_000_000_000))
        
 
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
        # # print("...")\
    pd.DataFrame(pipeline_img_dict).T.to_csv(results_path / f"{choice}_results.csv")
    accuracy = (correct/480)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    return  {"choice": choice,"accuracy": accuracy, "avgTimeToDetect": avgTimeToDetect, "medianTimeToDetect": medianTimeToDetect}


# print("is this optimized")
# print(cv.useOptimized())
def main(adjustment = "../", adjustment_on = False, input_path="data/images_copy", output_overall = "output/experimental_results/hough_iterative"
          ,output_timing ="output/timing_results", ground_truth="data/annotations/annotations.json", cli_printout:bool = True):
    if adjustment_on:
        input_path = adjustment + input_path
        output_overall = adjustment + output_overall
        output_timing = adjustment + output_timing
        ground_truth = adjustment + ground_truth

    
    overall_start = thread_time_ns()

# Open the ground truth annotations
    with open(ground_truth , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))

    # Get the pipeline configuration optionsß

    # Manually set this, (choice choice_time), so 0-3, and then 0 initially for choice_time, reset at the end of each for loop.
    choices = [("houghCircle",0), ("iterative",0)]

    updated = []
    results_list = []


    for choice, choice_time in choices:
        choice_start = thread_time_ns()
        # (DO A RUN HERE)
        results = pipelineTests([choice, input_path, file_data, output_overall])
        print(results)
        results_list.append(results)
        # save the big picture results
        choice_end =thread_time_ns()
        choice_time = choice_end - choice_start 
        updated.append([choice,choice_time])

    overall_end = thread_time_ns()
    overall_time = overall_end - overall_start

    txtStr = f"This pipeline runner took {overall_time} time in total. \n" 
    for option, option_time in updated:
        txtStr = txtStr + f"It spent {option_time} time on choice {option}. \n"


    # Ensure timing results directory exists
    timing_dir = Path(output_timing)
    timing_dir.mkdir(parents=True, exist_ok=True)

    # Create timing results file with properly formatted datetime
    timing_filename = timing_dir / f"timingResults_hough_iterative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(timing_filename, "w") as txt_file:
        txt_file.write(txtStr)
    if cli_printout:
        print(f"The summary statistics are saved in {output_overall} as .csvs \n \
                The timing info is saved as {str(timing_filename)}")
    return {"bigpicture0": f"{output_overall}/houghCircle_results.csv", 
            "bigpicture1":f"{output_overall}/iterative_results.csv", 
            "output_timing":str(timing_filename),
            "results": results_list}

if __name__ == "__main__":
    main()

# # push to readme
# # It differs from the binary_otsu experiment in that it's focused on the hough process rather than the explicit thresholding and blob detection processt \n\
# # It has saved the results of this in {output_overall}, where it will save the summary statistics in a folder called: {output_bp} and the individual results in a folder called {output_results}\n \
# # The summary statistics are named after their hyperparameter files, and are stored as .csv files. \n\
# # The results of each pipeline (ie each hyperparameter combination) are saved under a folder named after which thresholding method was used. \n \
# # These results are saved as a .csv file per combo, and list each image tested and their success or failure and dot count. \n\
# # Finally the total timing of each of these thresholding methods are saved in a txt file in the folder {output_timing}. \n \
# # This file is named timingResults_hough_alt_plain_[datetime].txt