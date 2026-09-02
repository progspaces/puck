#  Tkinter imports and set up, necessary before the rest of the imports for macOS
from tkinter import *
base = Tk()
base.tk.call('tk', 'scaling', 2.0)
## Name of the window you're opening
base.title('Tkinter Widget Size')
## 1920x1080, display size, +0+-1080 repositioning
base.geometry("1920x1080+0+-1080")
## set to be fullscrean
base.wm_attributes("-fullscreen", True)

## Other Imports
import cv2 as cv
from json import load
import importlib
from matplotlib import pyplot as plt
from collections import Counter


DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)

def area_of_frame(frame):
    x0 = frame[0][0]
    x1 = frame[1][0]
    y0 = frame[0][1]
    y1 = frame[1][1]
    return abs(y0-y1)* abs(x0-x1)

def bigger_smaller_frame(frame_0, frame_1):
 if area_of_frame(frame_0)> area_of_frame(frame_1):
    return (frame_0, frame_1)
 else:
    return (frame_1, frame_0)

def frame_to_polygon_list(frame):
    x0 = int(frame[0][0])
    x1 = int(frame[1][0])
    y0 = int(frame[0][1])
    y1 = int(frame[1][1])
    return [(x0,y0), (x0,y1), (x1,y1), (x1,y0)]

def frames(path):
    input = cv.imread(path)
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    ## grab the first two ids and their coordinates, that's all we're considering rn
    corners_a = corners[0][0]
    corners_b = corners[1][0]
    frame_0 = (corners_a[1], corners_b[3])
    frame_1 = (corners_a[3], corners_b[1])
    outer_frame, inner_frame = (bigger_smaller_frame(frame_0, frame_1))
    return (outer_frame, inner_frame, ids)

outer_frame, inner_frame, ids= frames("puck/apriltag_stills/test_0.png")
outer_polygon = frame_to_polygon_list(outer_frame)
inner_polygon = frame_to_polygon_list(inner_frame)

## Storage dictionaries and sets
program_lookup = {}
with open('puck/program_store/program_lookup.json') as f:
    program_lookup = dict(load(f))
recognized_in_run = set()
graphics_storage = dict()


def buffer(buffer, input):
    ''' 
    Literally just controls putting things into the buffer and 
    taking things out, a glorified function to pop and append.
    '''
    buffer.pop(0)
    buffer.append(input)
    return buffer

def max_freq(buffer):
    ''' 
    Grabs the most frequent Id in the buffer
    Then gives you back that most fequent ID
    and the coordinate of the last seen copy of that ID
    '''
    ids = [x[0] for x in buffer]
    most_freq = Counter(ids).most_common(1)[0][0]
    most_freq_coords = [x[1] for x in buffer if x[0]==most_freq][-1]
    return (most_freq, most_freq_coords)


def scale(cwidth, cheight, fheight, fwidth, coord_list):
    '''
    An attempt to scale the coordinate system to the webcam space 
    by taking in the width and height of the coordinates space
    and the width and height of the frames taken in
    and scaling all coordinates that are inputted in.
    '''
    scaled_list = [(int(pair[0] * (cwidth/fwidth)), int(pair[1] * (cheight/fheight)) ) for pair in coord_list]
    print(scaled_list)
    return scaled_list


def webcamManyCaptures(base,buffer_size = 35):
    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    fheight, fwidth, fchannel = frame.shape
    buffer_arr = [("Warming up",[(100,200),(100,400),(200,400),(200,200)])] * buffer_size
    v = StringVar(value= "Warming up") 
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()
    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0), outline='blue',fill="white", width=2)

    def handle_currently_recognized(current_recognized,v):
            int_form = int(current_recognized[0],5)
            if int_form >= 0 : ## in other words the int form is a good value and we like it.
                module_name = "puck.program_store." + program_lookup.get(str(int_form))##
                module = importlib.import_module(module_name)##
                if current_recognized[0] not in recognized_in_run:## Case one: We've never seen this ever before 
                    recognized_in_run.add(current_recognized[0])
                    graphics_storage.update({int_form:[]}) ## create an entry in the graphics storage
                    module.on_start(graphics_storage.get(int_form),canvas, box)
                    print("IT's A NEW PAPER")
                else: ## Case two: We have seen this before
                    previous = v.get()
                    if current_recognized[0] != previous:
                        ## if recognizing a new item, update the label.
                        v.set(current_recognized[0])
                    ## Okay now we need to check if it is a paper program
                    current = v.get()
                    print(f"Current is {current}")
                    v.set(current)
                    scaled = scale(cwidth = cwidth, cheight = cheight, fwidth = fwidth, fheight= fheight, coord_list=current_recognized[1])
                    canvas.coords(box, scaled)
                    module.on_update(graphics_storage.get(int_form),canvas, box)
            else:
                print("we do not have a valid program")
                int_form = -13 ## we do not have a valid programm associated with this
                print(current_recognized[0])
        else:
            # if current_recognized[0] not in recognized_in_run:## we've never seen this error, please add to the list
                # recognized_in_run.add(current_recognized[0])
            v.set(current_recognized[0])
            print(current_recognized[0])
            int_form = -12 ## this is not a paper as we recognize papers


    def update(cam,canvas, box):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        response = single_frame(frame,calibration_colours, rad_range)
        buffer(buffer_arr, response)
        canvas.itemconfig(tagOrId = text_label_replace, text=v.get())
        current_recognized = (max_freq(buffer_arr))
        handle_currently_recognized(current_recognized,v)
        if cv.waitKey(1) == ord('q'): ## stopping condition
            base.quit()
        base.after(10, update, cam, canvas, box)  # Timed Check, adding itself back onto the queue to run 20ms later

    base.after(20,update, cam, canvas, box)
    base.mainloop()
    print(recognized_in_run)
    print(graphics_storage)
    cam.release()
    cv.destroyAllWindows()


webcamManyCaptures()

