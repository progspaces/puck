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

    blur = list(range(blur_min,blur_max,blur_step))
    blob_area= list(range(area_min,area_max + area_step,area_step))
    blob_circ= list(np.arange(0,1,circ_step))

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

pipelines = ["src/puck/dotpipeline/binary0.json","src/puck/dotpipeline/adaptiveM0.json","src/puck/dotpipeline/adaptiveG0.json", "src/puck/dotpipeline/otsu0.json"]
choice = int(input("Please enter 0-3 to choose binary(0) or adaptiveM(1) or adaptiveG(2) or otsu(3): "))
print(generator(pipelines[choice])[0])