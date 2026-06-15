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

#calibration_colours are blah


def webcamCapture(save_path):
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


# webcamCapture("puck/output/test_frame.jpg")


cal_centers,cal_image = df.find_centers_hough("puck/output/test_cal.jpg", min_dist=CALIBRATION_MIN_DIST, minRadius=30, maxRadius=60)
colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords)

path = "puck/output/test_frame.jpg"
centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST,minRadius=0, maxRadius=60, grayscale=True)
colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
if len(colors_and_coords) ==4:
    black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
    # print(colors_and_coords)
    ordered_rectangle= clkwise.order_rectangle(colors_and_coords, black_dot[0])
    perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, calibration_colors,colorspace= "LUV")
    print(perm)
else:
      print("HELP")



# 1) get frame
# 2) get dots
# 3) get colors relative to calibration (ie assign a permutation)
# 4) open up json and search up what the permutation's assigned int is



with open(f'puck/output/polychrome_lookup.json', 'r') as fp:
    polychrome = dict(json.loads(fp.read()))

# print(dc.translate_perm_to_int(sample_perm,  polychrome.get(str(n_colours)) , n_colours))


