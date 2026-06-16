import json 
import cv2
import puck.code_modules.dot_finding.dot_finder as df
import puck.code_modules.sheet_creation.define_colourspace as dc
import puck.code_modules.colour_conversion.colour_finding as cf
import puck.code_modules.calibration.calibration as cal
import puck.code_modules.geometry.clockwise_dots as clkwise
import puck.code_modules.permutation_guessing.permutation_guessing as perm_guess

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
    colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords,n_colours)
    return calibration_colors

def single_frame_path(path, calibration_colors):
    centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST,minRadius=0, maxRadius=60, grayscale=True)
    colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
    if len(colors_and_coords) ==4:
        black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        try:
            ordered_rectangle = clkwise.order_rectangle(colors_and_coords, black_dot[0]) 
        except:
             print("error")## this is where the error is being thrown
        perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        print(perm)
        print(int(perm,n_colours))
    else:
        print("HELP, FOUR DOTS NOT FOUND")


def single_frame(frame, calibration_colors, n):
    centers,image = df.find_centers_hough_frames(frame, min_dist=PROGRAM_MIN_DIST,minRadius=0, maxRadius=60, grayscale=False)
    colors_and_coords=cf.get_colors_and_coords(centers,side = 10, image =image,colorspace= "RGB")
    if len(colors_and_coords) ==4:
        black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
        ordered_rectangle= clkwise.order_rectangle(colors_and_coords, black_dot[0])
        if type(ordered_rectangle) == dict:
            cv2.imwrite(f"puck/output/problem_frames/problem_frame{n}.jpg", frame)
            with open(f'puck/output/problem_frames/problem_frame{n}.json', 'w') as fp:
                json.dump(ordered_rectangle, fp, indent=3)
            print("SAVED")
            exit()
        perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, n_colours, calibration_colors,colorspace= "LUV")
        print(perm)
        print(int(perm,n_colours))
    else:
        print("HELP, FOUR DOTS NOT FOUND")




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
    while True:
        ret, frame = cam.read()

        cv2.imshow('Camera', frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        single_frame(frame,calibration_colours, n)
        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the capture and writer objects
    cam.release()
    # out.release()
    cv2.destroyAllWindows()

# webcamSingleCapture("puck/output/test_frame_p3_2.jpg")
calibration_colors = calibration_frame("puck/output/test_cal_p3.jpg")
single_frame_path("puck/output/test_frame_p3_2.jpg",calibration_colors) 
webcamManyCaptures(calibration_colors)
