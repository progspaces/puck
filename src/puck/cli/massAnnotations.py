import json
from annotator import run
import cv2 as cv
from sys import argv

def annotate(file_path):
    with open('src/puck/cli/annotations.json' , "r") as json_file:
        file_data = json.loads(json_file.read())

    ## start by writing to json
    if file_path not in file_data:
        file_data.update({file_path:run(file_path)})
    else:
        print("you've already annotated this, chose another image")
    print(file_data)
    with open('src/puck/cli/annotations.json', 'w') as fp:
        json.dump(file_data, fp)


cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
drawing = False  # true if mouse is pressed
    # Coordinate
x1, y1, x2, y2 = -1, -1, -1, -1
if len(argv) > 1:
    annotate(file_path=argv[1])
else:
    print("provide a file next time please")