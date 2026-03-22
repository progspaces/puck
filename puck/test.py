from code_modules.dot_finding.dot_finder import find_centers_hough
from pathlib import Path

a_paths = []
p = Path('.')
for path in p.glob("data/images_copy/dark/*/*/A/*[0-4].jpg"):
    a_paths.append(path)
sample = a_paths[23]
centers, image = find_centers_hough(sample,170)
print(centers)