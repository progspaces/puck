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

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]


def pipelineTests(args):
    p = Path('.')
    test_pipeline, choice, input_path, results_path, file_data= args
    results_path = Path("output/experimental_results/binary_otsu_pipeline_results/" + str(choice))
    results_path.mkdir(parents=True, exist_ok=True)
    # print(test_pipeline)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob(f'{input_path}/*/*/*/*/*[0].jpg'))):
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get("images"+str(img_path)[len(input_path):]))
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, test_pipeline[0])
        if choice == 0 : # binary
            gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
            _, thresholded = cv.threshold(gray, test_pipeline[3], 255, cv.THRESH_BINARY)
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
    
            # combine the masks with an OR so any pixel above either threshold counts as foreground
    
            # apply morphological transforms
            kernel = np.ones((3, 3), np.uint8)
            thresholded = cv.morphologyEx(np_mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
            thresholded= thresholded*255
            # # print(thresholded)
            thresholded = 255-thresholded
            
        blob_params = blobParamFunc(test_pipeline[1], test_pipeline[2])
        detector = cv.SimpleBlobDetector_create(blob_params)
        keypoints = detector.detect(thresholded)
        end = thread_time_ns()
        # # print(str(len(keypoints)) + " blobs detected")
        blank = np.zeros((1, 1))
        
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
        # # print("...")=
    pd.DataFrame(pipeline_img_dict).T.to_csv(results_path / (str(test_pipeline) + "_results.csv"))
    accuracy = (correct/480)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    return str(test_pipeline), (choice, accuracy, avgTimeToDetect, medianTimeToDetect)



def main(adjustment = "../", adjustment_on = False, input_path="data/images_copy", output_overall = "output/experimental_results/", output_results= "binary_otsu_pipeline_results", output_bp ="binary_otsu_big_picture" ,output_timing ="output/timing_results", ground_truth="data/annotations/annotations.json", cli_printout:bool = True):
    pipelines = ["experiments/best_thresholding/hyperparameters/binary0.json","experiments/best_thresholding/hyperparameters/otsu0.json"]
    new_pipelines =[]
    if adjustment_on:
        input_path = adjustment + input_path
        output_overall = adjustment + output_overall
        output_timing = adjustment + output_timing
        ground_truth = adjustment + ground_truth
        for p in pipelines:
            new_pipelines.append(adjustment + p) 
        pipelines = new_pipelines
    # Open the ground truth annotations
    with open(ground_truth , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))
        # print(json.loads(json_file.read()))

    overall_start = thread_time_ns()
    # Get the pipeline configuration options
    

    # Manually set this, (choice choice_time), so 0-3, and then 0 initially for choice_time, reset at the end of each for loop.
    choices = [(0,0),(1,0)]

    results_path = output_overall + output_results

    updated = []

    for choice, choice_time in choices:
        choice_start = thread_time_ns()
        pipeline_list_dict = {}
        with ThreadPoolExecutor(10) as pool:
            generatored_pipelines = generator(pipelines[choice])[1]
            list_of_choices = [choice] * len(generatored_pipelines)
            list_of_input_paths = [input_path] * len(generatored_pipelines)
            list_of_file_datas = [file_data] * len(generatored_pipelines)
            print(type(list_of_file_datas[1]))
            list_of_results_paths = [results_path]* len(generatored_pipelines)
            for name, result in tqdm(pool.map(pipelineTests, zip(generatored_pipelines, list_of_choices,list_of_input_paths,list_of_results_paths,list_of_file_datas)), total=len(generatored_pipelines)):
                pipeline_list_dict.update({name:result})

        # ensure that output directory exists for the big picture
        output_big_combo = output_overall + output_bp
        output_dir = Path(output_big_combo)        
        output_dir.mkdir(parents=True, exist_ok=True)

        # save the big picture results
        directory = str(pipelines[choice]).split("/")[-1][:-5]
        pd.DataFrame(pipeline_list_dict).T.to_csv(output_dir /( directory + "_results.csv"))
        choice_time = thread_time_ns() - choice_start
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
    timing_filename = timing_dir / f"timingResults_binary_otsu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(timing_filename, "w") as txt_file:
        txt_file.write(txtStr)

    if cli_printout:
        print(f"This has tested the hyperparameters generated by {pipelines[0]} and {pipelines[1]} \n \
It has saved the results of this in {output_overall}, where it will save the summary statistics in a folder called: {output_bp} and the individual results in a folder called {output_results}\n \
The total timing of each of these thresholding methods are saved in a txt file called {timing_filename} in the folder {output_timing}.")
        
    return {"bigpicture0": f"{output_overall}{output_bp}/binary0_results.csv", 
            "bigpicture1":f"{output_overall}{output_bp}/otsu0_results.csv", 
            "results0":f"{output_overall}{output_results}/0",
            "results1":f"{output_overall}{output_results}/1",
            "output_timing":str(timing_filename)}

if __name__ == "__main__":
    dict = main()
    print(dict)

## README
## The summary statistics are named after their hyperparameter files, and are stored as .csv files. \n\
## The results of each pipeline (ie each hyperparameter combination) are saved under a folder named after which thresholding method was used, for binary 0, for otsu 1. \n \
## These results are saved as a .csv file per combo, and list each image tested and their success or failure and dot count. \n\