import json
from annotator import run
import cv2 as cv

def annotate(file_path):
    cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
    drawing = False  # true if mouse is pressed
    # Coordinate
    x1, y1, x2, y2 = -1, -1, -1, -1
    with open('src/puck/cli/test.json' , "r") as json_file:
        file_data = json.loads(json_file.read())

    ## start by writing to json
    if file_path not in file_data:
        file_data.update({file_path:run(file_path)})
    print(file_data)
    with open('src/puck/cli/test.json', 'w') as fp:
        json.dump(file_data, fp)

annotate(file_path="puck/extraneous/initial_palette_tests/carter.50s.jpg")