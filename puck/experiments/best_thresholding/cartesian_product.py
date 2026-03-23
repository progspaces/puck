###
import json
import numpy as np
from itertools import product
import pprint

def generator(json_path):
    with open(json_path , "r") as json_file:
        parameters = dict(json.loads(json_file.read()))

    blur_min = parameters.get("blur_min")
    blur_max = parameters.get("blur_max")
    blur_step = parameters.get("blur_step")

    area_min = parameters.get("area_min")
    area_max = parameters.get("area_max")
    area_step = parameters.get("area_step")

    circ_step = parameters.get("circ_step")
    circ_min = parameters.get("circ_min")
    circ_max = parameters.get("circ_max")

    blur = list(range(blur_min,blur_max,blur_step))
    blob_area= list(range(area_min,area_max + area_step,area_step))
    blob_circ= list(np.arange(circ_min,circ_max,circ_step))
    blob_circ = np.round(blob_circ, 2)

    thresh = parameters.get("thresh")
    if thresh == "binary":
        binary_min = parameters.get("binary_min")
        binary_max = parameters.get("binary_max")
        binary_step = parameters.get("binary_step")
        binary_range = list(range(binary_min,binary_max,binary_step))
        p = list(product(blur,blob_area,blob_circ,binary_range))
    elif thresh == "adaptiveG" or thresh == "adaptiveM":
        block_size_min= parameters.get("block_size_min") # must be odd
        block_size_max= parameters.get("block_size_max") # must be odd
        block_size_range = list(range(block_size_min, block_size_max, 2))
        constant_min = parameters.get("constant_min")
        constant_max = parameters.get("constant_max")
        constant_step = parameters.get("constant_step")
        const_range = list(range(constant_min, constant_max, constant_step))
        p = list(product(blur,blob_area,blob_circ,block_size_range,const_range))
    else:
        p = list(product(blur,blob_area,blob_circ))
    return (thresh,p)

# print(generator("src/puck/dotpipeline/binary1.json")[1])


def houghGenerator(json_path):
    with open(json_path , "r") as json_file:
        parameters = dict(json.loads(json_file.read()))

    method = parameters.get("method")
    if method == "circle":
        dp_min = parameters.get("dp_min")
        dp_step = parameters.get("dp_step")
        dp_max = parameters.get("dp_max")
        dp_range = list(np.arange(dp_min,dp_max,dp_step))
        minDist_min = parameters.get("minDist_min")
        minDist_step = parameters.get("minDist_step")
        minDist_max = parameters.get("minDist_max")
        minDist_range = list(range(minDist_min,minDist_max,minDist_step))
        param1_min = parameters.get("param1_min")
        param1_step = parameters.get("param1_step")
        param1_max = parameters.get("param1_max")
        param1_range = list(range(param1_min,param1_max,param1_step))
        param2_min = parameters.get("param2_min")
        param2_step = parameters.get("param2_step")
        param2_max = parameters.get("param2_max")
        param2_range = list(range(param2_min,param2_max,param2_step))
        minRadius_min = parameters.get("minRadius_min")
        minRadius_step = parameters.get("minRadius_step")
        minRadius_max = parameters.get("minRadius_max")
        minRadius_range = list(range(minRadius_min,minRadius_max,minRadius_step))
        p = list(product(dp_range,minDist_range,param1_range,param2_range, minRadius_range))
    elif method == "circleAlt":
        dp_min = parameters.get("dp_min")
        dp_step = parameters.get("dp_step")
        dp_max = parameters.get("dp_max")
        dp_range = list(np.arange(dp_min,dp_max,dp_step))
        minDist_min = parameters.get("minDist_min")
        minDist_step = parameters.get("minDist_step")
        minDist_max = parameters.get("minDist_max")
        minDist_range = list(range(minDist_min,minDist_max,minDist_step))
        param1_min = parameters.get("param1_min")
        param1_step = parameters.get("param1_step")
        param1_max = parameters.get("param1_max")
        param1_range = list(range(param1_min,param1_max,param1_step))
        param2_min = parameters.get("param2_min")
        param2_step = parameters.get("param2_step")
        param2_max = parameters.get("param2_max")
        param2_range = list(np.arange(param2_min,param2_max,param2_step))
        minRadius_min = parameters.get("minRadius_min")
        minRadius_step = parameters.get("minRadius_step")
        minRadius_max = parameters.get("minRadius_max")
        minRadius_range = list(range(minRadius_min,minRadius_max,minRadius_step))
        p = list(product(dp_range,minDist_range,param1_range,param2_range, minRadius_range))
    elif method == "ellipse" :
        sigma_min = parameters.get("sigma_min")
        sigma_step = parameters.get("sigma_step")
        sigma_max = parameters.get("sigma_max")
        sigma_range = list(np.arange(sigma_min,sigma_max,sigma_step))
        low_threshold_min = parameters.get("low_threshold_min")
        low_threshold_step = parameters.get("low_threshold_step")
        low_threshold_max = parameters.get("low_threshold_max")
        low_threshold_range = list(np.arange(low_threshold_min,low_threshold_max,low_threshold_step))
        high_threshold_min = parameters.get("high_threshold_min")
        high_threshold_step = parameters.get("high_threshold_step")
        high_threshold_max = parameters.get("high_threshold_max")
        high_threshold_range = list(np.arange(high_threshold_min,high_threshold_max,high_threshold_step))
        accuracy_min = parameters.get("accuracy_min")
        accuracy_step = parameters.get("accuracy_step")
        accuracy_max = parameters.get("accuracy_max")
        accuracy_range = list(range(accuracy_min,accuracy_max,accuracy_step))
        threshold_min = parameters.get("threshold_min")
        threshold_step = parameters.get("threshold_step")
        threshold_max = parameters.get("threshold_max")
        threshold_range = list(range(threshold_min,threshold_max,threshold_step))
        min_size_min = parameters.get("min_size_min")
        min_size_step = parameters.get("min_size_step")
        min_size_max = parameters.get("min_size_max")
        min_size_range = list(range(min_size_min,min_size_max,min_size_step))
        print(threshold_range)
        p = list(product(sigma_range,low_threshold_range,high_threshold_range,accuracy_range,threshold_range,min_size_range))
        p = [combo for combo in p if combo[1] < combo[2]]
    return (method,p)

# print(houghGenerator("src/puck/dotpipeline/hyperparameters/houghEllipse.json"))