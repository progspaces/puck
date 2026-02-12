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


def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]



def pipelineTests():
    results_path = Path("./results/houghMultiTest")
    results_path.mkdir(parents=True, exist_ok=True)
    # print(test_pipeline)
    correct = 0 
    times = []
    pipeline_img_dict = {}
    for img_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        print(str(img_path)[:-4])
        start = thread_time_ns()
        gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
        image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
        imageBlurred = cv.medianBlur(image, 9)
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        rows = gray.shape[0]
        print(rows)
        circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                        param1=100, param2=30,
                        minRadius=10, maxRadius=30)[:,:,0:2][0]
        end = thread_time_ns()
        point_list = [(float(c[0]),float(c[1])) for c in circles]
        point_list.sort(key= lambda p: math.dist(p, (0,0)))
        gtkp.sort(key= lambda p: math.dist(p, (0,0)))
 
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
    choice_results_path = results_path / str(3)
    choice_results_path.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(pipeline_img_dict).T.to_csv(choice_results_path / "hough_results.csv")
    accuracy = (correct/480)
    avgTimeToDetect = statistics.mean(times)
    medianTimeToDetect = statistics.median(times)
    return str("test_pipeline"), (3, accuracy, avgTimeToDetect, medianTimeToDetect)




overall_start = thread_time_ns()

# Open the ground truth annotations
with open('./src/puck/datacollection/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

# Get the pipeline configuration options

p = Path('.')


image = cv.imread("/Users/jdreiling/Desktop/puck/puck/images/custom/jack_cole/medium/B/custom_jack_cole_medium_B_0.jpg", cv.IMREAD_COLOR_RGB)
imageBlurred = cv.medianBlur(image, 9)
gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
rows = gray.shape[0]
print(rows)

pipelineTests()

    


