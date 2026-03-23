# cal_path = "/Users/jdreiling/Desktop/puck/puck/images_calibration/high/custom/jack_cole/high_custom_jack_cole_calibration.jpg"
import code_modules
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import code_modules.dot_finding.dot_finder as df
import code_modules.colour_conversion.colour_finding as cf


CALIBRATION_MIN_DIST = 30
PROGRAM_MIN_DIST = 170
cal_path ="puck/images_calibration/medium/dark/jack_cole/medium_dark_jack_cole_calibration.jpg"
cal_centers,cal_image = df.find_centers_hough(cal_path, min_dist=CALIBRATION_MIN_DIST)
colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]

calibration_colors =get_calibration_colors(black_dot_cal_coords,colors_and_coords)
calibration_colors


a_paths = []
b_paths = []
c_paths = []
d_paths = []

p = Path('..')

for path in p.glob("images/dark/*/*/A/*_A*[0-4].jpg"):
    a_paths.append("/Users/jdreiling/Desktop/puck/puck/" + str(path)[2:])


for path in p.glob("images/dark/*/*/B/*_B*[0-4].jpg"):
    b_paths.append("/Users/jdreiling/Desktop/puck/puck/" + str(path)[2:])

for path in p.glob("images/dark/*/*/C/*_C*[0-4].jpg"):
    c_paths.append("/Users/jdreiling/Desktop/puck/puck/" + str(path)[2:])

for path in p.glob("images/dark/*/*/D/*_D*[0-4].jpg"):
    d_paths.append("/Users/jdreiling/Desktop/puck/puck/" + str(path)[2:])

path_perm_dict = {"a": (a_paths, 'afd'),"b": (b_paths, 'ahc'),"c": (c_paths, 'ebg'),"d": (d_paths, 'fff') }

checking_dict =[]
for k in path_perm_dict.keys():
    paths, true_perm = path_perm_dict.get(k)
    for path in paths:
        centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST)
        # print(path)
        if(path == "/Users/jdreiling/Desktop/puck/puck//images/dark/davids/high/C/dark_davids_high_C_3.jpg"):
            out = image.copy()
            plt.imshow(out)
            plt.show()
        colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
        if len(colors_and_coords) ==4:
            black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
            # colored_coords = [c for c in colors_and_coords if c is not black_dot]
            # print(colored_coords)
            print(colors_and_coords)
            ordered_rectangle= order_rectangle(colors_and_coords, black_dot[0])
            perm = cf.get_color_perm(ordered_rectangle, calibration_colors,colorspace= "LUV")
            correct = (perm == true_perm)
            overlap =sum([(perm[i] == true_perm[i]) for i in range(0,len(perm))])
        checking_dict.append({"key":k, "path":path, "found_perm": perm, "true_perm": true_perm, "correct": correct, "overlap":overlap})

results_df = pd.DataFrame(checking_dict, columns=["key","path", "found_perm", "true_perm", "correct", "overlap"])


results_df.to_csv("../results/program_recognition_results_dark.csv")
