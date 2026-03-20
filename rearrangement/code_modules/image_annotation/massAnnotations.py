import json
from annotator import run
import cv2 as cv
from sys import argv
from pathlib import Path

def annotate(p):
    with open('src/puck/cli/annotations.json' , "r") as json_file:
        file_data = json.loads(json_file.read())
    for file_path in sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg'))):
        annotate_this_img = True
        file_path_str = str(file_path)
        if file_path_str not in file_data:
            file_data.update({file_path_str:run(file_path_str)})
            print("Continue? Please press q to quit, r to redo your annotation, any other key to continue.")
            while annotate_this_img:
              k = cv.waitKey()
              if k == ord("r"): 
                file_data.update({file_path_str:run(file_path_str)})
                print("Continue? Please press q to quit, r to redo your annotation, any other key to continue.")
              else:
                annotate_this_img = False
                print(f"You pressed key {k}")
                with open('src/puck/cli/annotations.json', 'w') as fp:
                  json.dump(file_data, fp)
                if k == ord("q"):
                  print("Bye-bye! *a small elvish spirit waves as they destroy hours of your work*")
                  return



cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
drawing = False  # true if mouse is pressed
    # Coordinate
x1, y1, x2, y2 = -1, -1, -1, -1
p = Path('.')
print("Please annotate these images. \n " \
"Start with the black dot and then go clockwise, shortways and then longways and then shortways around the box \n " \
"Use your mouse to find the radius, then drag to reach the edge. If you are unsatisfied with the circle drawn you can \n" \
"restart by simply clicking again. Once you are satisfied, press enter and move to the next circle. Ignore the elvish spirits.")
annotate(p)
