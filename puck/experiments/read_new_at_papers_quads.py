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
from actor import Actor, DrawingActor

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





def draw_triangle(self, drawing_actor):
    self.send_to(drawing_actor, {"action": "new", "info": [(0,0), (2,0), (1,1)]})
    time.sleep(1)
    __, message= self.read()
    triangle_id = message.get("info")
    self.send_to(drawing_actor,{"action": "update", "id": triangle_id,"info": [(0,0), (4,0), (2,2)]})


def draw_loop(self, canvas):
    message_type = None
    while True:
        sender, new_message = self.read()
        print(new_message)
        message_type = new_message.get("type")
        if message_type == "kill":
            exit()
        elif message_type == "action":
            message_action = new_message.get("action")
            message_info = new_message.get("info")
            if message_action == "new":
                id = canvas.create_polygon(message_info, outline='blue',fill="white", width=2)
                self.send_to(sender,{"type": "canvas_id", "info": id})
                print("sent some information yayyyyyyyyyyy")

def test_run(self, drawing_actor):
    message_type = None
    while True:
        sender, new_message = self.read()
        print(new_message)
        message_type = new_message.get("type")
        if message_type == "kill":
            exit()
        elif message_type == "new_shape":
            message_info = new_message.get("info")
            print(f"message_info {message_info}")
            self.send_to(drawing_actor, {"type": "action", "action": "new", "info": message_info})
        elif message_type == "canvas_id":
            print(new_message.get("info"))

def handle_currently_recognized(program_encoding,current_coords, drawing_actor):
        if program_encoding is not None: ## in other words the int form is a good value and we like it.
            module_name = "puck.program_store." + program_lookup.get(str(program_encoding))##
            module = importlib.import_module(module_name) ##
            if program_encoding not in encoding_to_actor: ## Case one: We've never seen this ever before 
                t = Actor(test_run, drawing_actor)
                t.start()
                encoding_to_actor[program_encoding] = t
                t.read_only_message({"type": "new_shape", "info": current_coords})
            # Case two we have seen this before and the thread is running.
            else:
                t = encoding_to_actor.get(program_encoding)
            # t.read_only_message({"type":"coordinates","info":current_coords})


def handle_raw_ids(ids,coords,drawing_actor):
    if ids is not None:
        program_encoding = int("".join(map(str, ids)),4)
        if program_encoding == 192 or program_encoding == 48 or program_encoding == 12:
            program_encoding = 3
        print(program_encoding)
        handle_currently_recognized(program_encoding,coords,drawing_actor)
        return program_encoding
    else:
        return None

def webcamManyCaptures(base,buffer_size = 35):
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()

    drawing_actor = DrawingActor(draw_loop, canvas)
    encoding_to_actor["drawing_actor"]= drawing_actor
    drawing_actor.start()

    cam = cv.VideoCapture(0)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    papers_and_ids = paper_frame_based(frame)
    for paper, id, in papers_and_ids:
        program_encoding = handle_raw_ids(id, paper, drawing_actor)
    v = StringVar(value= str(program_encoding)) 

    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    # box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0), outline='blue',fill="white", width=2)
            
    def update(cam, canvas):
        _, frame = cam.read()
        window_name = "Second Monitor Window"
        cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
        cv.moveWindow(window_name, 0, 300)
        cv.resizeWindow(window_name, 600, 500)
        cv.imshow(window_name, frame)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        pre_existing_encodings = set(encoding_to_actor.copy().keys())
        pre_existing_encodings.remove("drawing_actor") ## we do not want to be rid of the drawing actor unless q is pressed
        for coords, ids in paper_frame_based(frame):
        ## whatever it "sees" is "in the scene" by this point. whatever it doesn't "see" should be killed off.
        # for coords, ids in frames_frame_based(frame): ## needs to return a list of tuples
            program_encoding = handle_raw_ids(ids, coords, drawing_actor)
            if program_encoding is not None: pre_existing_encodings.discard(program_encoding) 
                ## using discard so it doesn't throw an error when pre_existing_encodings doesn't have it
                ## use remove to throw an error when the set of pre_existing_encordings doesn't have it.
        #     # canvas.coords(box, frame_to_polygon_list(avg_box)) ## outline of paper
        for encoding in (pre_existing_encodings):
            actor = encoding_to_actor.get(encoding)
            actor.end()
        if cv.waitKey(1) == ord('q'): ## stopping condition
            existing_encodings = set(encoding_to_actor.copy().values())
            for e in existing_encodings:
                e.end()
            print("done with the joining and the exiting")
            base.quit()
        base.after(10, update, cam, canvas)  # Timed Check, adding itself back onto the queue to run 20ms later
        
    base.after(20,update, cam, canvas)
    base.mainloop()
    cam.release()
    cv.destroyAllWindows()

webcamManyCaptures(base= base)