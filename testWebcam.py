import cv2

imageOrVideo = "video"

def camera( imgOrVid:str = "",runNumber:int = 0, grabFrames:bool= False, grabFrameRate:int =10):
    ''''
    Runs webcam and gets the input
    If you want a singular photo taken, set imgOrVid to "image", else it will start a video
    Please set the run number according to which run you want to store this as.
    If you want to store frames from the video, set grabFrames to true, else it will not store anything
    Set the grabFrameRate for videos, to decide at what rate to grab frames.
    '''
    ## Grabbed base code from https://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python
    vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
    # returns a viedos capture object called vc
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read() # returns a value (boolean I think? true) and frame
        if imgOrVid == "image" and rval != False: ## if image is the input, takes a singular photo
            cv2.imwrite(f"frames/run{runNumber}snapshot.jpg", frame)
        else: ## otherwise start a camera feed
            count = 0
            while rval:
                cv2.imshow("preview", frame)
                rval, frame = vc.read() 
                # returns the retreval value and the image
                # combines grab and retrive in one call. if nothing grabbed, returns false.
                if count % grabFrameRate == 0 and grabFrames == True and rval != False: 
                ## if grabframes is true, then store frames from the camera feed at the rate specified
                    cv2.imwrite(f"frames/run{runNumber}frame{count}.jpg", frame) 
                    ## this is storing all of them in the frames folder under rum#frame#.jpg
                count +=1
                key = cv2.waitKey(20)
                if key == 27: # exit on ESC
                    break
    else:
        rval = False

    cv2.destroyWindow("preview")
    vc.release()    

camera(imageOrVideo)