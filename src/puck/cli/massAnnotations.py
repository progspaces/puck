import json
from annotator import run
import cv2 as cv
from sys import argv
from pathlib import Path

def annotate(p):
    with open('src/puck/cli/annotations.json' , "r") as json_file:
        file_data = json.loads(json_file.read())
    for file_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        stop = False
        file_path_str = str(file_path)
        if file_path_str not in file_data:
            file_data.update({file_path_str:run(file_path_str)})
            print("i've updated stuff")
            print(file_data)
            print("continue or no? press q for quit, r for a redo, any other key to continue")
            while (stop == False):
              k = cv.waitKey()
              if k == ord("r"): 
                file_data.update({file_path_str:run(file_path_str)})
                print("i've updated stuff")
                print(file_data)
                print("continue or no? press q for quit, r for a redo, any other key to continue")
              elif k == ord("q"):
                with open('src/puck/cli/annotations.json', 'w') as fp:
                  json.dump(file_data, fp)
                end = True
                stop = True
              else:
                print(f"k is {k}")
                stop = True
        else:
            print("you've already annotated this, let's do the next image")
            continue
        if end == True:
           break
        with open('src/puck/cli/annotations.json', 'w') as fp:
            json.dump(file_data, fp)


cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
drawing = False  # true if mouse is pressed
    # Coordinate
x1, y1, x2, y2 = -1, -1, -1, -1
p = Path('.')
annotate(p)
