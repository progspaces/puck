import cv2

imageOrVideo = "video"

def camera(grabFrames, grabFrameRate, grabFrameRun, imgOrVid):
    ## Grabbed from https://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python
    vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
    # returns a viedo capture object called vc

    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read() # returns a value (boolean I think? true) and frame
        if imgOrVid == "image":
            cv2.imwrite(f"frames/run{grabFrameRun}snapshot.jpg", frame)
        else:
            count = 0
            while rval:
                cv2.imshow("preview", frame)
                rval, frame = vc.read() # returns the retreval value, and then. the image 
                if count % grabFrameRate == 0 and grabFrames == True:
                    print("blahs")
                    cv2.imwrite(f"frames/run{grabFrameRun}frame{count}.jpg", frame)
                count +=1
                # combines grab and retrive in one call. if nothing grabbed, returns false.
                key = cv2.waitKey(20)
                if key == 27: # exit on ESC
                    break
    else:
        rval = False

    cv2.destroyWindow("preview")
    vc.release()    

camera(False,100,1, imageOrVideo)