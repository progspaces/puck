# import json 
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

CALIBRATION_MIN_DIST = 20
PROGRAM_MIN_DIST= 100
n_colours = 3

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

def calibration_frame(path, tolerance):
    print("please click and drag your mouse around one of the calibration circles, so we have an approximent size of the circle from the camera's perspective")
    rad_range = draw_circle_get_range(path,tolerance)
    cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=True)
    while cal_centers == [] :
        print("the sought for circles are not the size specified, please redraw them")
        rad_range = draw_circle_get_range(path,tolerance)
        cal_centers,cal_image = find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]),grayscale=True)

                # while True:
    #     cv2.imshow("cal image returned", cal_image)
    #     if cv2.waitKey(0) == ord('q'):
    #          break
    # cv2.destroyWindow("cal image returned")
    colors_and_coords=get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    pprint(f"colors and coords {colors_and_coords}")
    black_dot_cal_coords = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    calibration_colors =get_calibration_colors(black_dot_cal_coords,colors_and_coords,n_colours)
    return calibration_colors, rad_range

def single_frame_path(path, calibration_colors, rad_range = (17,22), image_colorsaved= "RGB"):
    centers,image = find_centers_hough(path, min_dist=PROGRAM_MIN_DIST,minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]), grayscale=False,image_colorsaved=image_colorsaved)
    while True:
        cv2.imshow("image returned", image)
        if cv2.waitKey(0) == ord('q'):
             break
    cv2.destroyWindow("image returned")
    colors_and_coords=get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
    pprint(colors_and_coords)
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        print(perm)
        return (int(perm,n_colours))
    elif not found_rectangle:
        return "not rectangular" ## error code for not rectangular 
    else:
        return "not 4 dots" ## error code for not 4 dots


def check_coords(colors_and_coords):
     rect = [[pair[0] for pair in colors_and_coords ]][0]
     return len(get_all_rects(rect)) >0


def single_frame(frame, calibration_colors, rad_range = (17,21)):
    centers,image = find_centers_hough_frames(frame, min_dist=PROGRAM_MIN_DIST,minRadius=int(rad_range[0]), maxRadius=int(rad_range[1]), grayscale=False)
    colors_and_coords=get_colors_and_coords(centers,side = 10, image =image,colorspace= "RGB")
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        # print(perm)
        return (int(perm,n_colours))
    elif not found_rectangle:
        return "not rectangular" # error code for not a rectangle
    else:
        return "not 4 dots" ## error code for not 4 dots


def buffer(buffer, input):
    buffer.pop(0)
    buffer.append(input)
    return buffer

def max_freq(buffer):
    return (Counter(buffer).most_common(1)[0][0])


def webcamManyCaptures(calibration_colours):
    # Open the default camera
    cam = cv2.VideoCapture(0)

    # Get the default frame width and height
    # frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
    n = 6 + 13
    buffer_arr = [0] * 100
    while True:
        ret, frame = cam.read()

        cv2.imshow('Camera', frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        response = single_frame(frame,calibration_colours, n)
        print(max_freq(buffer(buffer_arr, response)))
        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the capture and writer objects
    cam.release()
    # out.release()
    cv2.destroyAllWindows()


def draw_circle_get_range(image,tolerance):
    return run_radius(image,tolerance)


calibration_colors, rad_range = calibration_frame("puck/output/test_cal_p3.jpg", .2)
path1 = "puck/output/problem_frames/problem_frame14.jpg"
single_frame_path(path1,calibration_colors, rad_range = rad_range, image_colorsaved = "BGR") 
