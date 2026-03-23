import code_modules.dot_finding.dot_finder as df
import code_modules.colour_conversion.colour_finding as cf
import code_modules.calibration.calibration as cal
import code_modules.geometry.clockwise_dots as clkwise
import code_modules.permutation_guessing.permutation_guessing as perm

from pathlib import Path

a_paths = []
p = Path('.')
for path in p.glob("data/images_copy/dark/*/*/A/*[0-4].jpg"):
    a_paths.append(path)
sample = a_paths[23]
centers, image = df.find_centers_hough(sample,170)
img_colors_and_coords= cf.get_colors_and_coords(centers, 25, image, "RGB")
img_black_dot = cf.get_black_dot(img_colors_and_coords, "rgb")


CALIBRATION_MIN_DIST=30
cal_path ="data/images_calibration/medium/dark/jack_cole/medium_dark_jack_cole_calibration.jpg"
cal_centers,cal_image = df.find_centers_hough(cal_path, min_dist=CALIBRATION_MIN_DIST)
colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]

calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords)
ordered_rectangle= clkwise.order_rectangle(img_colors_and_coords, img_black_dot[0])


print(perm.get_color_perm(ordered_rectangle, calibration_colors))
