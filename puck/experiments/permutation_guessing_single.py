
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import puck.code_modules.dot_finding.dot_finder as df
import puck.code_modules.colour_conversion.colour_finding as cf
import puck.code_modules.calibration.calibration as cal
import puck.code_modules.geometry.clockwise_dots as clkwise
import puck.code_modules.permutation_guessing.permutation_guessing as perm_guess

## CONSTANTS
CALIBRATION_MIN_DIST = 30
PROGRAM_MIN_DIST = 170


def main(palette = "custom", results_prefix =  "puck/output/program_recognition_results_", adjustment = "../", adjustment_on = True):
    cal_path ="puck/data/images_calibration/high/"+ palette+ "/jack_cole/high_" + palette + "_jack_cole_calibration.jpg"
    results_path = results_prefix + palette + ".csv"
    if adjustment_on:
        results_path = adjustment + results_path
        cal_path = adjustment + cal_path
    cal_centers,cal_image = df.find_centers_hough(cal_path, min_dist=CALIBRATION_MIN_DIST)
    colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    # calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords)
    p = Path('../')
    path =[path for path in p.glob("puck/data/images_copy/" + palette + "/davids/short/B/*_B_0.jpg")][0]
    print(path)

    path_perm_dict = {"b": ([path], 'ahc')}
    for k in path_perm_dict.keys():
        paths, true_perm = path_perm_dict.get(k)
        for path in paths:
            centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST, grayscale=True)
    #         colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
    #         if len(colors_and_coords) ==4:
    #             black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")

    #             print(colors_and_coords)
    #             ordered_rectangle= clkwise.order_rectangle(colors_and_coords, black_dot[0])
    #             perm = perm_guess.get_color_perm(ordered_rectangle, calibration_colors,colorspace= "LUV")
    #             correct = (perm == true_perm)
    #             overlap =sum([(perm[i] == true_perm[i]) for i in range(0,len(perm))])
    #         checking_dict.append({"key":k, "path":path, "found_perm": perm, "true_perm": true_perm, "correct": correct, "overlap":overlap})

    # print(results_path)
    # results_df = pd.DataFrame(checking_dict, columns=["key","path", "found_perm", "true_perm", "correct", "overlap"])
    # results_df.to_csv(results_path)

    # print(f"Results of testing the {palette} palette, have been put into a .csv in the output folder.")
    # print(f"It can be found at: {results_path}.")


    # return results_path

if __name__ == "__main__":
    main(palette= "custom")