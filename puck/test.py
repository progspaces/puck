import code_modules.dot_finding.dot_finder as df
import code_modules.colour_conversion.colour_finding as cf
from pathlib import Path

a_paths = []
p = Path('.')
for path in p.glob("data/images_copy/dark/*/*/A/*[0-4].jpg"):
    a_paths.append(path)
sample = a_paths[23]
centers, image = df.find_centers_hough(sample,170)
colors_and_coords = cf.get_colors_and_coords(centers, 25, image, "RGB")
black_dot = cf.get_black_dot(colors_and_coords, "rgb")
print(black_dot)