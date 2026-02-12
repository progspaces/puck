


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
from skimage.feature import canny
from skimage.transform import hough_ellipse
from skimage.draw import ellipse_perimeter



p = Path('.')
img_path = "images/custom/jack_cole/medium/B/custom_jack_cole_medium_B_4.jpg"
image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
print("loaded image")
imageBlurred = cv.medianBlur(image, 3)
print("blurred")
gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
print('grayed')
edges = canny(gray, sigma=3, low_threshold=.5, high_threshold=.8)
print("edges")
result = hough_ellipse(edges, accuracy=30, threshold=100, min_size=1, max_size=200)
print("ellipsified")
circles = result.sort(order='accumulator')       
print(circles)

