import json 
import cv2
import puck.code_modules.dot_finding.dot_finder as df
import puck.code_modules.sheet_creation.define_colourspace as dc
import puck.code_modules.colour_conversion.colour_finding as cf
import puck.code_modules.calibration.calibration as cal
import puck.code_modules.geometry.clockwise_dots as clkwise
import puck.code_modules.geometry.rectangles as rectangles
import puck.code_modules.permutation_guessing.permutation_guessing as perm_guess
import pprint
import collections

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

def calibration_frame(path):
    cal_centers,cal_image = df.find_centers_hough(path, min_dist=CALIBRATION_MIN_DIST, minRadius=10, maxRadius=60,grayscale=True)
    while True:
        cv2.imshow("cal image returned", cal_image)
        if cv2.waitKey(0) == ord('q'):
             break
    cv2.destroyWindow("cal image returned")
    colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    pprint.pprint(f"colors and coords {colors_and_coords}")
    black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords,n_colours)
    return calibration_colors

def single_frame_path(path, calibration_colors,image_colorsaved= "RGB"):
    centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST,minRadius=0, maxRadius=60, grayscale=False,image_colorsaved=image_colorsaved)
    while True:
        cv2.imshow("image returned", image)
        if cv2.waitKey(0) == ord('q'):
             break
    cv2.destroyWindow("image returned")
    colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
    pprint.pprint(colors_and_coords)
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = clkwise.order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        print(perm)
        return (int(perm,n_colours))
    elif not found_rectangle:
        return -1 ## error code for not rectangular 
    else:
        return -2 ## error code for not 4 dots


def check_coords(colors_and_coords):
     rect = [[pair[0] for pair in colors_and_coords ]][0]
     return len(rectangles.get_all_rects(rect)) >0


def single_frame(frame, calibration_colors, n):
    centers,image = df.find_centers_hough_frames(frame, min_dist=PROGRAM_MIN_DIST,minRadius=0, maxRadius=60, grayscale=False)
    colors_and_coords=cf.get_colors_and_coords(centers,side = 10, image =image,colorspace= "RGB")
    found_rectangle = check_coords(colors_and_coords)
    if len(colors_and_coords) ==4 and found_rectangle:
        black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle = clkwise.order_rectangle(colors_and_coords, black_dot[0]) 
        perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        # print(perm)
        return (int(perm,n_colours))
    elif not found_rectangle:
        return -1 # error code for not a rectangle
    else:
        return -2 ## error code for not 4 dots


def buffer(buffer, input):
    buffer.pop(0)
    buffer.append(input)
    return buffer

def max_freq(buffer):
    return (collections.Counter(buffer).most_common(1)[0][0])


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

# webcamSingleCapture("puck/output/test_frame_p3_2.jpg")
calibration_colors = calibration_frame("puck/output/test_cal_p3.jpg")
# path1 = "puck/output/problem_frames/problem_frame14.jpg"
# path2 = path1[:-4] + "_test.jpg"
webcamManyCaptures(calibration_colors)



# single_frame_path(path1,calibration_colors, image_colorsaved = "BGR") 
# single_frame_path(path1,calibration_colors, image_colorsaved = "RGB") 

# single_frame_path(path2,calibration_colors) 

# counter = 0
# for i in range(7,20):
#     single_frame_path(f"puck/output/problem_frames/problem_frame{i}.jpg",calibration_colors) 
# # webcamManyCaptures(calibration_colors)


