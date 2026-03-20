from pathlib import Path
from pprint import pprint
import cv2 as cv
p = Path('.')
# pprint(list(p.glob('images/*/*/*/*/*[0-4].jpg')))
a = sorted(list(p.glob('images/*/*/*/*/*[0-4].jpg')))
print(str(a[3]))
cv.namedWindow('image', cv.WND_PROP_ASPECT_RATIO)
img = cv.imread(str(a[3]))
cv.imshow('image', img)
k = cv.waitKey(0)

