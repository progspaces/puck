# import json 
from tkinter import *
base = Tk()
base.tk.call('tk', 'scaling', 2.0)
base.title('Tkinter Widget Size')
base.geometry("1920x1080+0+-1080")
base.wm_attributes("-fullscreen", True)

## Errors
NOT_4_DOTS = "not 4 dots"
NOT_RECT = "not rectangular"
NOT_SEEING_FULL_DOTS = "can't see all dots properly",
WARMING_UP = "Warming up"

# import threading
# from puck.graphics.paper_recognition_prints import recognize
# permutation = None
# paper_coordinates = None
# stop_tk = False
# drawing_thread = threading.Thread(target = recognize, kwargs={"base":base,"permutation":permutation, 
                                        #   "paper_coordinates":paper_coordinates, "stop_tk":stop_tk})

import cv2
from puck.code_modules.dot_finding.dot_finder import find_centers_hough, find_centers_hough_frames
from puck.code_modules.colour_conversion.colour_finding import get_colors_and_coords, get_black_dot
from puck.code_modules.calibration.calibration import get_calibration_colors
from puck.code_modules.geometry.clockwise_dots import order_rectangle
from puck.code_modules.geometry.rectangles import get_all_rects
from puck.code_modules.permutation_guessing.permutation_guessing import get_color_perm_and_dist
from pprint import pprint
from collections import Counter
from puck.image_annotation.annotator import run_radius
from statistics import mean
from json import load
import importlib

CALIBRATION_MIN_DIST = 20
PROGRAM_MIN_DIST= 100
n_colours = 3

program_lookup = {}
with open('puck/program_store/program_lookup.json') as f:
    program_lookup = dict(load(f))

recognized_in_run = set()
graphics_storage = dict()

def webcamSingleCapture(save_path):
    i = 0
    vc = cv2.VideoCapture(0) 
    if vc.isOpened(): 
        rval, frame = vc.read() 
        cv2.imshow("preview", frame)
        while True:
            key = cv2.waitKey(0)
            print("HIHIHIHIHIHI")
            print(key)
            rval, frame = vc.read() 
            if not rval:
                    print("Something is wrong with the camera, rval is false, press a key when fixed")
            elif key == 112:  ##  press p
                    cv2.imshow("preview", frame)
            elif key == 32: #space to capture
                    cv2.imwrite(save_path, frame)
                    break
    cv2.destroyWindow("preview")
    vc.release()    

def calibration_frame(path, tolerance, radius_already_set = False):
    print("please click and drag your mouse around one of the calibration circles, so we have an approximent size of the circle from the camera's perspective," \
    "press enter when you are satisfied with your circle. click again to draw a new circle.")
    if radius_already_set:
        rad_range = [16,21]
    else:
        rad_range = draw_circle_get_range(path,tolerance, "image BALHHHH")
    cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=False)
    while len(cal_centers) < 9:
        print("the sought for circles are not the size specified, please redraw them")
        rad_range = draw_circle_get_range(path,tolerance, "awoeuhroiewhf")
        cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=False)

                # while True:
    #     cv2.imshow("cal image returned", cal_image)
    #     if cv2.waitKey(0) == ord('q'):
    #          break
    # cv2.destroyWindow("cal image returned")
    colors_and_coords=get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    # pprint(f"colors and coords {colors_and_coords}")
    black_dot_cal_coords = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    calibration_colors =get_calibration_colors(black_dot_cal_coords,colors_and_coords,n_colours)
    return calibration_colors, rad_range

def single_frame_path(path, calibration_colors, rad_range = (17,22), image_colorsaved= "RGB"):
    centers,image = find_centers_hough(path, min_dist=PROGRAM_MIN_DIST,minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]), grayscale=False,image_colorsaved=image_colorsaved, image_show = True)
    while True:
        cv2.imshow("image returned", image)
        if cv2.waitKey(0) == ord('q'):
            break
    cv2.destroyWindow("image returned")
    colors_and_coords=get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
    # pprint(colors_and_coords)
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        coords_only = ([x[0] for x in ordered_rectangle])
        return (perm,coords_only)
    elif not found_rectangle:
        return (NOT_RECT, [(0,0),(0,0),(0,0),(0,0)]) ## error code for not rectangular 
    else:
        return (NOT_SEEING_FULL_DOTS,[(0,0),(0,0),(0,0),(0,0)]) ## error code for not 4 dots


def check_coords(colors_and_coords):
     rect = [[pair[0] for pair in colors_and_coords ]][0]
     return len(get_all_rects(rect)) >0


def single_frame(frame, calibration_colors, rad_range = (17,21)):
    centers,image = find_centers_hough_frames(frame, min_dist=PROGRAM_MIN_DIST,minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]), grayscale=False)
    try:
        colors_and_coords=get_colors_and_coords(centers,side = 10, image =image,colorspace= "RGB")
    except:
        return (NOT_SEEING_FULL_DOTS, [(0,0), (0,50), (50,50),(50,0)])
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        # print(perm)
        coords_only = ([black_dot[0]] + [x[0] for x in ordered_rectangle])
        return (perm,coords_only)
    elif not found_rectangle:
        return (NOT_RECT, [(0,0), (0,50), (50,50),(50,0)]) # error code for not a rectangle
    else:
        return (NOT_4_DOTS,[(0,0), (0,50), (50,50),(50,0)]) ## error code for not 4 dots


def buffer(buffer, input):
    buffer.pop(0)
    buffer.append(input)
    # print(f"this is the buffer {buffer}")
    return buffer

def max_freq(buffer):
    ids = [x[0] for x in buffer]
    most_freq = Counter(ids).most_common(1)[0][0]
    most_freq_coords = [x[1] for x in buffer if x[0]==most_freq][-1]
    # printq(most_freq)
    # print(f"{most_freq_coords}")
    #  print(len(most_freq_coords))

    # x0, y0 = most_freq_coords[0]
    # x1, y1 = most_freq_coords[1]
    # x2, y2 = most_freq_coords[2]
    # x3, y3 = most_freq_coords[3]
    
    # x0= int(mean([coord[0][0] for coord in most_freq_coords]))
    # y0= int(mean([coord[0][1] for coord in most_freq_coords]))

    # x1= int(mean([coord[1][0] for coord in most_freq_coords]))
    # y1= int(mean([coord[1][1] for coord in most_freq_coords]))

    # x2= int(mean([coord[2][0]for coord in most_freq_coords]))
    # y2= int(mean([coord[2][1] for coord in most_freq_coords]))


    # x3= int(mean([coord[3][0]for coord in most_freq_coords]))
    # y3= int(mean([coord[3][1] for coord in most_freq_coords]))
    ### CHECK THAT THIS COMES IN THE RIGHT ORDER, IT SHOULD BECAUSE IT SHOULD BE CLOCKWISE
    return (most_freq, most_freq_coords) #  return (Counter(buffer).most_common(1)[0][0])


def scale(cwidth, cheight, fheight, fwidth, coord_list):
    scaled_list = [(int(pair[0] * (cwidth/fwidth)), int(pair[1] * (cheight/fheight)) ) for pair in coord_list]
    print(scaled_list)
    return scaled_list

def webcamManyCaptures(calibration_colours, rad_range,base):
    # Open the default camera
    ## Setup elements
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    fheight, fwidth, fchannel = frame.shape
    # print(f"{fheight} , {fwidth}")
    buffer_arr = [("Warming up",[(100,200),(100,400),(200,400),(200,200)])] * 35
    v = StringVar() 
    v.set("Warming up")
    cheight = 1080
    cwidth =  1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()
    text_label_replace = canvas.create_text((200,50),text=v.get(),font=("Helvetica", 50), fill= "White")
    box = canvas.create_polygon((0,0), (0,0), (0,0), (0,0),
                          outline='blue',fill="white", width=2)


    def combined_errors(value):
        return value != NOT_4_DOTS and value != WARMING_UP and value != NOT_RECT and value != NOT_SEEING_FULL_DOTS

    def run_spawn(value):
            item_dict = {}
            int_form = int(value,n_colours)
            module_name = "puck.program_store." + program_lookup.get(str(int_form))
            module = importlib.import_module(module_name)
            graphics_storage.update({int_form:[]})
            module.on_start(graphics_storage.get(int_form),canvas, box)
            return module
            
        

    def handle_currently_recognized(current_recognized,v):
        ## Case one: We've never seen this ever before 
        if current_recognized[0] not in recognized_in_run:
            recognized_in_run.add(current_recognized[0])
            if combined_errors(current_recognized[0]): ## it is a paper and thus might have code that needs you to spawn graphics
                run_spawn(value = current_recognized[0])
                print("IT's A NEW PAPER")
            ## Else, it is not a paper and you do not need to spawn anything as it is one of the combined errors
        ## Case two: We have seen this before
        else:
            ## Now we need to check if it's changed from the previous or not
            previous = v.get()
            if current_recognized[0] != previous:
                         ## if recognizing a new item, update the label.
                v.set(current_recognized[0])
            ## Okay now we need to check if it is a paper program
            current = v.get()
            print(f"Current is {current}")
            v.set(current)
            if combined_errors(current_recognized[0]):
                int_form = int(current_recognized[0],n_colours)
                scaled = scale(cwidth = cwidth, cheight = cheight, fwidth = fwidth, fheight= fheight, coord_list=current_recognized[1])
                canvas.coords(box, scaled)
                if int_form >= 0 and int_form <= 2 or int_form == 7 or int_form == 9: ## in other words the int form is a good value and we like it.
                    module_name = "puck.program_store." + program_lookup.get(str(int_form))
                    module = importlib.import_module(module_name)
                    module.on_update(graphics_storage.get(int_form),canvas, box)
            else:
                int_form = -12


    def update(cam,canvas, box):
        ret, frame = cam.read()
        fheight, fwidth, fchannel = (frame.shape)
        window_name = "Second Monitor Window"
        cv2.namedWindow(window_name, cv2.WINDOW_FREERATIO,)
        cv2.moveWindow(window_name, 0, 300)
        cv2.resizeWindow(window_name, 600, 500)
        cv2.imshow(window_name, frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        response = single_frame(frame,calibration_colours, rad_range)
        buffer(buffer_arr, response)
        canvas.itemconfig(tagOrId = text_label_replace, text=v.get())
        current_recognized = (max_freq(buffer_arr))
        # print(f"currently recognized: {current_recognized}")
        handle_currently_recognized(current_recognized,v)
        if cv2.waitKey(1) == ord('q'): ## stopping condition
            base.quit()
        base.after(10, update, cam, canvas, box)  # Timed Check, adding itself back onto the queue to run 20ms later

    base.after(20,update, cam, canvas, box)
    base.mainloop()
    print(recognized_in_run)
    print(graphics_storage)
    cam.release()
    cv2.destroyAllWindows()


def webcamVideoCalibration(tolerance):
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        cv2.imshow('Camera', frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        calibration_colors, rad_range = calibration_frame(frame,tolerance)
        if cv2.waitKey(1) == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    return calibration_colors, rad_range

def draw_circle_get_range(image,tolerance, name):
    return run_radius(image,tolerance, name)


calibration_colors, rad_range = calibration_frame("puck/output/test_cal_p3.jpg", .2, radius_already_set=True)
webcamManyCaptures(calibration_colors, rad_range,base)