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

def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.minCircularity = minCircularity
    params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]

# Open the ground truth annotations
with open('./src/puck/cli/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))

# Get the pipeline configuration options

p = Path('.')


img_path = "images/custom/davids/high/A/custom_davids_high_A_1.jpg"
start = thread_time_ns()
gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
plt.imshow(image)
plt.show()
imageBlurred = cv.medianBlur(image, 9)
gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
plt.imshow(gray,cmap="gray")
plt.show()
# print(gray)



# use Otsu's method to find the thresholds for hue and saturation
_, thresh_h = cv.threshold(image_hsv[:, :, 0],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
_, thresh_v = cv.threshold(image_hsv[:, :, 2],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

# mask the image to get determine which pixels with hue and saturation above their thresholds
mask_v= image_hsv[:, :, 1] > thresh_v
mask_h= image_hsv[:, :, 1] > thresh_h


# # combine the masks with an OR so any pixel above either threshold counts as foreground
# np_mask = np.logical_or(mask_h, mask_v)

#     # apply morphological transforms
# kernel = np.ones((3, 3), np.uint8)
# thresholded = cv.morphologyEx(np_mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
# thresholded= thresholded*255
# # # print(thresholded)
# thresholded = 255-thresholded

    
# blob_params = blobParamFunc(500, .8)
# detector = cv.SimpleBlobDetector_create(blob_params)
# keypoints = detector.detect(thresholded)
# end = thread_time_ns()
# # # print(str(len(keypoints)) + " blobs detected")
# blank = np.zeros((1, 1))
# blobs = cv.drawKeypoints(image, keypoints, blank, (255, 0, 0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

       
