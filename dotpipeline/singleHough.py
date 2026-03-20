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

with open('./src/puck/cli/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

img_path = "images/custom/davids/high/D/custom_davids_high_D_1.jpg"
print(str(img_path)[:-4])
gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
imageBlurred = cv.medianBlur(image, 9)
gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
rows = gray.shape[0]
circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                        param1=100, param2=30,
                        minRadius=10, maxRadius=30)[:,:,0:2][0]
centers = [(float(c[0]),float(c[1])) for c in circles]
centers.sort(key= lambda p: math.dist(p, (0,0)))
gtkp.sort(key= lambda p: math.dist(p, (0,0)))
print(gtkp)
print(centers)