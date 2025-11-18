import cv2
## Grabbed from https://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python


cv2.namedWindow("preview")
vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
# returns a viedo capture object called vc

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read() # returns a value (boolean I think? true) and frame
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read() # returns the retreval value, and then. the image 
    # combines grab and retrive in one call. if nothing grabbed, returns false.
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()