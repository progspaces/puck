import itertools
from pipelineGenerator import generator
from pathlib import Path
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import json
import math


def blobParamFunc(minArea, minCircularity):
    params = cv.SimpleBlobDetector_Params()
    # params.filterByCircularity = True
    # params.minCircularity = minCircularity
    # params.minArea=minArea
    params.blobColor = 0
    return params

def groundTruthKeyPoints(entry):
    return [tuple(point[1:3]) for point in entry]


with open('./src/puck/cli/annotations.json' , "r") as json_file:
    file_data = dict(json.loads(json_file.read()))


pipelines = ["src/puck/dotpipeline/binary0.json","src/puck/dotpipeline/adaptiveM0.json","src/puck/dotpipeline/adaptiveG0.json", "src/puck/dotpipeline/otsu0.json"]
choice = int(input("Please enter 0-3 to choose binary(0) or adaptiveM(1) or adaptiveG(2) or otsu(3): "))
pipeline_list = (generator(pipelines[choice]))[1]
test_pipeline = pipeline_list[0]
print(test_pipeline)

p = Path('.')
# for test_pipeline in pipeline_list:
correct = 0 
# for img_path in sorted(list(p.glob('images/*/*/*/*/*[0].jpg'))):
for x in range(1,2,1):
    img_path = "images/custom/davids/short/B/custom_davids_short_B_0.jpg"
    gtkp = groundTruthKeyPoints(file_data.get(str(img_path)))
    image = cv.imread(img_path, cv.IMREAD_COLOR_RGB)
    imageBlurred = cv.medianBlur(image, test_pipeline[0])
    thresholded =0

    if choice == 0 : # binary
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        _, thresholded = cv.threshold(gray, test_pipeline[3], 255, cv.THRESH_BINARY)
        print(thresholded.dtype)
        plt.imshow(thresholded, cmap="gray")
        plt.show()
    elif choice == 1: ## Adaptive Mean
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        # thresholded = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,test_pipeline[3],test_pipeline[4])
        thresholded = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
        thresholded = cv.fastNlMeansDenoising(thresholded)
        print("THRESHOLDED")
        plt.imshow(thresholded, cmap="gray")
        plt.show()
    elif choice == 2: ## Adaptive Gaussian
        gray = cv.cvtColor(imageBlurred, cv.COLOR_RGBA2GRAY)
        # thresholded = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,test_pipeline[3],test_pipeline[4])
        thresholded = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,11,2)
        plt.imshow(thresholded, cmap="gray")
        plt.show()
        print("THRESHOLDED")
    else: 
        pass
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
 
        # apply morphological transforms
        # for mt in self.morph_transform:
        kernel = np.ones((3, 3), np.uint8)
        thresholded = cv.morphologyEx(np_mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
        # thresholded = 255-thresholded
        plt.imshow(thresholded, cmap="gray")
        plt.show()
        print("THRESHOLDED")

        


    blob_params = blobParamFunc(test_pipeline[1], test_pipeline[2])
    detector = cv.SimpleBlobDetector_create()
    keypoints = detector.detect(thresholded)
    print(str(len(keypoints)) + " blobs detected")

    circles = cv.HoughCircles(thresholded, cv.HOUGH_GRADIENT,dp=1,minDist=2,maxRadius =1000)
    print("circles")
    print(circles)

    contours, hierarchy = cv.findContours(thresholded, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    print('contours')
    print(contours)
    cv.drawContours(imageBlurred, contours, -1, (0,255,0), 10)
    plt.imshow(imageBlurred, cmap="gray")
    plt.show()

    blank = np.zeros((1, 1))
    blobs = cv.drawKeypoints(image, keypoints, blank, (255, 0, 0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    accuracy = []
    for kp in keypoints:
        closest = (100000, (0,0))
        point = (kp.pt)
        for gt in gtkp:
            distance = math.dist(gt, point)
            if distance < closest[0]:
                closest= (distance, gt)
        accuracy.append(closest[0])
    print(accuracy)
    if accuracy < [5,5,5,5] and len(accuracy) == 4:
        print(accuracy)
        correct +=1
    # plt.imshow(blobs, interpolation="nearest")
    # plt.show()
print(correct)

## blob will be the same across the board


