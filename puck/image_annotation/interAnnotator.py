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

#grab the dot, the id of the image, chose x or y, get the value for that.

a_list = []
b_list = []
c_list = []

for img in list(julia_dict.keys()):
        a = julia_dict.get(img)
        b = david_dict.get(img)
        c = michael_dict.get(img)
        for num in range(0,4,1):
                ## letter [num] gets you back the whole entry
                a_entry = a[num]
                b_entry = b[num]
                c_entry = c[num]
                for ind in range(1,3):
                        # grabs the x and the y as 1 and 2
                        a_list.append(a_entry[ind])
                        b_list.append(b_entry[ind])
                        c_list.append(c_entry[ind])

full = [a_list, b_list, c_list]