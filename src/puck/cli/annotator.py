import math
import numpy as np
import cv2 as cv
import os


cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
drawing = False  # true if mouse is pressed
 # Coordinate
x1, y1, x2, y2 = -1, -1, -1, -1

def run(imgPath):
    outputPath = imgPath[:-4] + "_annotated.jpg"
    annotationList = []
    img = cv.imread(imgPath)        
    cv.imshow('image', img)
    # Create a layer to draw circle. The layer has the same dimension of image
    layer = np.zeros((img.shape[0], img.shape[1], 3), dtype="uint8")

   # mouse callback function
    def draw_circle(event, x, y, flags, param):
      global x1, y1, x2, y2, drawing,holdx, holdy
      # Manage different button state
      if event == cv.EVENT_LBUTTONDOWN:
          ## SETS THE DRAWING TO BE TRUE SO THAT WHEN YOU SIZE IT RESIZES
          drawing = True
          x1, y1 = x, y
      elif event == cv.EVENT_MOUSEMOVE:
          ## CONSTANTLY REDRAWS THE CIRCLE WHILE YOU'RE RESIZING IT
          if drawing == True:
              # Fill all value to 0 to clean layer
              layer.fill(0)
              cv.circle(layer, (x1, y1),calc_radius(x1, y1, x, y), (255, 0, 0), 1)
              # Create a mask of shape
              img2gray = cv.cvtColor(layer, cv.COLOR_BGR2GRAY)
              ret, mask = cv.threshold(img2gray, 0, 255, cv.THRESH_BINARY)
              # Create a copy of original image
              _img = img.copy()
              # Set the value of mask to 0, to avoid color overlap problems
              _img[np.where(mask)] = 0
              cv.imshow('image', np.where(layer == 0, _img, layer))
      elif event == cv.EVENT_LBUTTONUP:
            drawing = False
            layer.fill(0)
            radius = calc_radius(x1, y1, x, y)
            holdx= x
            holdy = y
            cv.circle(layer, (x1, y1), radius, (255, 0, 0), 1)
            # Create a mask of shape
            img2gray = cv.cvtColor(layer, cv.COLOR_BGR2GRAY)
            ret, mask = cv.threshold(img2gray, 0, 255, cv.THRESH_BINARY)
            _img = img.copy()
            # Set the value of mask to 0, to avoid color overlap problems
            _img[np.where(mask)] = 0
            # Merge two array using Numpy where function
            print(f"x is {x1}")
            print(f"y is {y1}")
            print(f"radius is {radius}")
            cv.imshow('image', np.where(layer == 0, _img, layer))

  # Assig callback 
    cv.setMouseCallback('image', draw_circle)

 # Service function to calculate radius (Pythagorean theorem) 
    def calc_radius(x1, y1, x2, y2):
      delta_x = abs(x2 - x1)
      delta_y = abs(y2 - y1)
      return int(math.sqrt((delta_x**2)+(delta_y**2)))

    while True:
      k = cv.waitKey(1)
      if k == ord('a'):
          print("you've hit a")
      elif k == 13:
         #SAVES THE location
         radius = calc_radius(x1, y1, holdx, holdy)
         label = input("Describe this pixel using one word (e.g. dog) and press ENTER: ")
         text_x_pos = x1 + radius
         text_y_pos = y1
         cv.circle(img, (x1, y1), radius, (255, 0, 0), 1)
         cv.putText(img, label, (text_x_pos,text_y_pos), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
         print(f"x is {x1}, y is {y1}, radius is {radius}, and the label is {label}")
         entry = (label,x1,y1,radius)
         annotationList.append(entry)
         print("saves the location go to next thing")
      elif k == 27: # ESE to terminate a program
          cv.imwrite(outputPath, img)
          cv.destroyAllWindows()
          break
    return (annotationList)



