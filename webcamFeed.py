import cv2
vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
    # returns a viedos capture object called vc
if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read() #
    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read() 
        key = cv2.waitKey(20)
        if key == 32: # exit on ESC
            cv2.imwrite(f"snapshot.jpg", frame)
        elif key == 27: # exit on ESC
            break

cv2.destroyWindow("preview")
vc.release()    