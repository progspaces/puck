
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import code_modules.dot_finding.dot_finder as df
import code_modules.colour_conversion.colour_finding as cf
import code_modules.calibration.calibration as cal
import code_modules.geometry.clockwise_dots as clkwise
import code_modules.permutation_guessing.permutation_guessing as perm

## CONSTANTS
CALIBRATION_MIN_DIST = 30
PROGRAM_MIN_DIST = 170
PAL = "dark"
results_path = "../output/program_recognition_results_"+ PAL + ".csv"


cal_path ="puck/images_calibration/medium/"+ PAL+ "/jack_cole/medium_" + PAL + "_jack_cole_calibration.jpg"
cal_centers,cal_image = df.find_centers_hough(cal_path, min_dist=CALIBRATION_MIN_DIST)
colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords)

p = Path('..')

a_paths =[path for path in p.glob("images/" + PAL + "/*/*/A/*_A*[0-4].jpg")]
b_paths =[path for path in p.glob("images/" + PAL + "/*/*/B/*_B*[0-4].jpg")]
c_paths =[path for path in p.glob("images/"+ PAL + "/*/*/C/*_C*[0-4].jpg")]
d_paths =[path for path in p.glob("images/"+ PAL + "/*/*/D/*_D*[0-4].jpg")]

path_perm_dict = {"a": (a_paths, 'afd'),"b": (b_paths, 'ahc'),"c": (c_paths, 'ebg'),"d": (d_paths, 'fff') }

checking_dict =[]
for k in path_perm_dict.keys():
    paths, true_perm = path_perm_dict.get(k)
    for path in paths:
        centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST)
        colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
        if len(colors_and_coords) ==4:
            black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")

            print(colors_and_coords)
            ordered_rectangle= clkwise.order_rectangle(colors_and_coords, black_dot[0])
            perm = cf.get_color_perm(ordered_rectangle, calibration_colors,colorspace= "LUV")
            correct = (perm == true_perm)
            overlap =sum([(perm[i] == true_perm[i]) for i in range(0,len(perm))])
        checking_dict.append({"key":k, "path":path, "found_perm": perm, "true_perm": true_perm, "correct": correct, "overlap":overlap})

results_df = pd.DataFrame(checking_dict, columns=["key","path", "found_perm", "true_perm", "correct", "overlap"])
results_df.to_csv(results_path)
print(f"Results of testing the {PAL} palette, have been put into a .csv in the output folder.")
print(f"It can be found at: {results_path}.")

