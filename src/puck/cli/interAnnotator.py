import json
import cv2 as cv
from pathlib import Path
import krippendorff
import pprint

julias_path = "/Users/jdreiling/Desktop/puck/puck/src/puck/cli/annotations_julia.json"
davids_path = "/Users/jdreiling/Desktop/puck/puck/src/puck/cli/annotations_david.json"
michaels_path = "/Users/jdreiling/Desktop/puck/puck/src/puck/cli/annotations_michael.json"


with open(julias_path , "r") as json_file_julia:
        julia_dict = dict(json.loads(json_file_julia.read()))

with open(davids_path , "r") as json_file_davids:
        david_dict = dict(json.loads(json_file_davids.read()))

with open(michaels_path , "r") as json_file_michael:
        michael_dict = dict(json.loads(json_file_michael.read()))

test = (list(julia_dict.keys())[0])
print(julia_dict.get(test))
print(david_dict.get(test))
print(michael_dict.get(test))

annotations = {}

for img in list(julia_dict.keys()):
        a = julia_dict.get(img)
        b = david_dict.get(img)
        c = michael_dict.get(img)
        annotations.update({img: (a,b,c)})

print(annotations)
# krippendorff.alpha(
#         reliablity_data = ,
#         value_counts = ,
#         value_domain = ,
#         level_of_measurment = 
# )