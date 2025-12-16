import json
from annotator import run
import cv2 as cv
from sys import argv
from pathlib import Path

def annotate(p):
    with open('src/puck/cli/annotations.json' , "r") as json_file:
        file_data = json.loads(json_file.read())
    for file_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        if file_path not in file_data:
            file_data.update({file_path:run(file_path)})
        else:
            print("you've already annotated this, let's do the next image")
            continue
    with open('src/puck/cli/annotations.json', 'w') as fp:
        json.dump(file_data, fp)


cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
drawing = False  # true if mouse is pressed
    # Coordinate
x1, y1, x2, y2 = -1, -1, -1, -1
p = Path('.')
annotate(p)
