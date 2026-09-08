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
import threading 
import time
from actor import Actor

DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
program_lookup = {}
with open('puck/program_store/program_lookup.json') as f:
    program_lookup = dict(load(f))
encoding_to_actor = dict()
graphics_storage = dict()


def average_pt(corners):
    sum_x = 0
    sum_y = 0 
    for pair in corners:
        sum_x += pair[0]
        sum_y += pair[1]
    return (int(sum_x/4), int(sum_y/4))

def paper_frame_based(frame):
    input = frame
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    if ids is not None and len(ids)==4:
        bads = [x for x in ids if x>4]
        if len(bads) >0 :
                ## SAVE WHERE IT SEES THE BAD THING
                copy = cv.aruco.drawDetectedMarkers(input, corners, ids)
                plt.figimage = copy
                plt.savefig('test.png') ##??
        corners_a = corners[0][0]
        corners_b = corners[1][0]
        corners_c = corners[2][0]
        corners_d = corners[3][0]
        averaged_paper = [average_pt(corners_a),
                          average_pt(corners_b),
                          average_pt(corners_d),
                          average_pt(corners_c)]
        return [(averaged_paper, ids)]
    else:
        return[(None,None)]


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


def draw_loop(self, drawing_actor):
    message_type = None
    while True:
        sender, new_message = self.read()
        print(new_message)
        message_type = new_message.get("type")
        if message_type == "kill":
            exit()
        self.send_to(sender,{"type": "canvas_id", "info": 7})


def draw_triangle(self, drawing_actor):
    self.send_to(drawing_actor, {"action": "new", "info": [(0,0), (2,0), (1,1)]})
    time.sleep(1)
    __, message= self.read()
    triangle_id = message.get("info")
    self.send_to(drawing_actor,{"action": "update", "id": triangle_id,"info": [(0,0), (4,0), (2,2)]})


def webcamManyCaptures(base,buffer_size = 35):
    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    paper_frame_based(frame)
    v = StringVar(value= "Warming up") 
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()
    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    # box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0), outline='blue',fill="white", width=2)


    drawing_actor = Actor(draw_loop, None)
    encoding_to_actor["drawing_actor"]= drawing_actor
    drawing_actor.start()
    global_actor = Actor(draw_loop, None)
    encoding_to_actor["global_actor"]= global_actor
    global_actor.start()
    # actor_one = Actor(draw_triangle, drawing_actor)
    # encoding_to_actor["actor_one"]= actor_one
    # actor_one.start()

    def handle_currently_recognized(program_encoding,current_coords):
            if program_encoding is not None: ## in other words the int form is a good value and we like it.
                module_name = "puck.program_store." + program_lookup.get(str(program_encoding))##
                module = importlib.import_module(module_name) ##
                if program_encoding not in encoding_to_actor: ## Case one: We've never seen this ever before 
                    t = Actor(draw_triangle, drawing_actor)
                    t.start()
                    encoding_to_actor[program_encoding] = t
                # Case two we have seen this before and the thread is running.
                ## TODO: Send message of current coords somehow 
                else:
                    t = encoding_to_actor.get(program_encoding)
                global_actor.send_to(t,{"type":"coordinates","info":current_coords})

            
    def update(cam, canvas):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        pre_existing_encodings = set(encoding_to_actor.copy().keys())
        for coords, ids in paper_frame_based(frame):
        ## whatever it "sees" is "in the scene" by this point. whatever it doesn't "see" should be killed off.
        # for coords, ids in frames_frame_based(frame): ## needs to return a list of tuples
            if ids is not None:
                program_encoding = int("".join(map(str, ids)),4)
                if program_encoding == 192 or program_encoding == 48 or program_encoding == 12:
                    program_encoding = 3
                print(program_encoding)
                print(coords)
                pre_existing_encodings.discard(program_encoding) 
                ## using discard so it doesn't throw an error when pre_existing_encodings doesn't have it
                ## use remove to throw an error when the set of pre_existing_encordings doesn't have it.
                handle_currently_recognized(program_encoding,coords)
        #     # canvas.coords(box, frame_to_polygon_list(avg_box)) ## outline of paper
        for encoding in (pre_existing_encodings):
            actor = encoding_to_actor.get(encoding)
            actor.end()
            actor.join()
        if cv.waitKey(1) == ord('q'): ## stopping condition
            existing_encodings = set(encoding_to_actor.copy().values())
            for e in existing_encodings:
                e.end()
                e.join()
            print("done with the joining and the exiting")
            base.quit()
        base.after(10, update, cam, canvas)  # Timed Check, adding itself back onto the queue to run 20ms later
        
    base.after(20,update, cam, canvas)
    base.mainloop()
    cam.release()
    cv.destroyAllWindows()

webcamManyCaptures(base= base)