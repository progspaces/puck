## read in calibration image

import cv2
from itertools import product
import cv2
import click
from itertools import product
import os

PALETTES = ["custom", "dark"]
DISTS = ["high", "medium", "short"]
ROOMS = ["john_honey","jack_cole","davids", "michaels", ]

variants = product(ROOMS,DISTS,PALETTES)
def webcamCapture():
    i = 0
    vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
        # returns a viedos capture object called vc
    # thread1 = Thread(target = showPreview)
    if vc.isOpened(): # try to get the first frame
        # thread1.start()
        for palette,room,dist in variants: 
            directory = f"{room}/{dist}/{palette}/"
            file_name = f"{room}_{dist}_{palette}_calibration.jpg"
            os.makedirs(directory,exist_ok=True)
            path_name = directory + file_name
            rval, frame = vc.read() 
            cv2.imshow("preview", frame)
            while True:
                print(f"Press space to take {path_name}")
                key = cv2.waitKey(0)
                print("HIHIHIHIHIHI")
                print(key)
                rval, frame = vc.read() 
                if not rval:
                    print("Something is wrong with the camera, rval is false, press a key when fixed")
                elif key == 9:
                    cv2.imshow("preview", frame)
                elif key == 32: #space to capture
                    cv2.imwrite(f"{path_name}", frame)
                    break
    cv2.destroyWindow("preview")
    vc.release()    

webcamCapture()