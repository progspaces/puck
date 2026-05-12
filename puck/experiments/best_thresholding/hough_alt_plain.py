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
from puck.experiments.best_thresholding.cartesian_product import houghGenerator
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter

## A file to check the hyper parameters of CV as well as compare the houghCircle function in OpenCV to the scikit-image hough_ellipse function.
## Use hyper paremter files, houghCircle.json for cv and houghEllispe.json for scikit




def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]




def pipelineTests(args):
    p = Path('.')
    test_pipeline , choice, input_path, file_data, results_path = args
    results_path = Path(f"{results_path}")
    results_path.mkdir(parents=True, exist_ok=True)
    # print(test_pipeline)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob(f'{input_path}/*/*/*/*/*[0].jpg'))):
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get("images"+ str(img_path)[len(input_path):]))
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 3)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        if choice == "houghCircle":
            rows = gray.shape[0]
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT,
                                     int(test_pipeline[0]), test_pipeline[1],
                            param1=test_pipeline[2], param2=test_pipeline[3],
                            minRadius=test_pipeline[4], maxRadius=30)
            circles = circles[:,:,0:2][0] if circles is not None else []
        elif choice == "houghCircleAlt":
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT_ALT, test_pipeline[0], test_pipeline[1],
                            param1=test_pipeline[2], param2=test_pipeline[3],
                            minRadius=test_pipeline[4], maxRadius=30)
            circles = circles[:,:,0:2][0] if circles is not None else []
        elif choice == "houghEllipse":
            edges = canny(gray, sigma=test_pipeline[0], low_threshold=test_pipeline[1], high_threshold=test_pipeline[2])
            result = hough_ellipse(edges, accuracy=test_pipeline[3], threshold=test_pipeline[4], min_size=test_pipeline[5], max_size=120)
            circles = result.sort(order='accumulator')
        end = thread_time_ns()
        # print(test_pipeline, str(img_path)[:-4] , str((end-start)/1_000_000_000))
        point_list = [(float(c[0]),float(c[1])) for c in circles]
 
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

    choice_results_path = results_path / choice
    choice_results_path.mkdir(parents=True, exist_ok=True)
    file_name =  str(test_pipeline)+ "hough_results.csv"
    pd.DataFrame(pipeline_img_dict).T.to_csv(choice_results_path / file_name)
    accuracy = (correct/480)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    return str(test_pipeline), (choice, accuracy, avgTimeToDetect, medianTimeToDetect)


# print("is this optimized")
# print(cv.useOptimized())
def main(adjustment = "../", adjustment_on = False,input_path="data/images_copy", output_overall = "output/experimental_results/", 
         output_results= "hough_options", output_bp ="hough_options_big_picture" ,output_timing ="output/timing_results", ground_truth="./data/annotations/annotations.json", cli_printout:bool = True):
    pipelines = ["/experiments/best_thresholding/hyperparameters/houghCircle.json","/experiments/best_thresholding/hyperparameters/houghCircleAlt.json"]
    new_pipelines =[]
    if adjustment_on:
        input_path = adjustment + input_path
        output_overall = adjustment + output_overall
        output_timing = adjustment + output_timing
        ground_truth = adjustment + ground_truth
        for p in pipelines:
            new_pipelines.append(adjustment + p) 
        pipelines = new_pipelines 

    
    overall_start = thread_time_ns()

# Open the ground truth annotations
    with open(ground_truth , "r") as json_file:
        file_data = dict(json.loads(json_file.read()))

    # Get the pipeline configuration optionsß

    # Manually set this, (choice choice_time), so 0-3, and then 0 initially for choice_time, reset at the end of each for loop.
    choices = [("houghCircle",0), ("houghCircleAlt",0)]

    updated = []
    results_path = output_overall + output_results




    for choice, choice_time in choices:
        choice_start = thread_time_ns()
        pipeline_list_dict = {}
        with ThreadPoolExecutor(10) as pool:
            # call a function on each item in a list and handle results
            generated_pipelines = houghGenerator("../experiments/best_thresholding/hyperparameters/"+ choice + ".json")[1]
            list_of_choices = [choice] * len(generated_pipelines)
            list_of_input_paths = [input_path] * len(generated_pipelines)
            list_of_file_datas = [file_data] * len(generated_pipelines)
            list_of_results_paths = [results_path]* len(generated_pipelines)
            for name, result in tqdm(pool.map(pipelineTests, zip(generated_pipelines,list_of_choices, list_of_input_paths, list_of_file_datas, list_of_results_paths)), total=len(generated_pipelines)):
                pipeline_list_dict.update({name:result})   

        # ensure that output directory exists for the big picture
        output_dir = Path(f"{output_overall}{output_bp}")        
        output_dir.mkdir(parents=True, exist_ok=True)

        # save the big picture results
        choice_results = choice +  "_results.csv"
        pd.DataFrame(pipeline_list_dict).T.to_csv(output_dir / choice_results)
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
    timing_filename = timing_dir / f"timingResults_hough_alt_plain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(timing_filename, "w") as txt_file:
        txt_file.write(txtStr)
    if cli_printout:
        print(f"This has tested the hyperparameters generated by {pipelines[0]} and {pipelines[1]} \n \
The summary statistics are saved in {output_overall}{output_bp} as a .csv \n \
The tested pipelines are saved as many individual .csv files in {output_overall}{output_results}/houghCircle[Alt] \n \
The timing info is saved as {str(timing_filename)}")
    return {"bigpicture0": f"{output_overall}{output_bp}/houghCircle_results.csv", 
            "bigpicture1":f"{output_overall}{output_bp}/houghCircleAlt_results.csv", 
            "results0":f"{output_overall}{output_results}/houghCircle",
            "results1":f"{output_overall}{output_results}/houghCircleAlt",
            "output_timing":str(timing_filename)}

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