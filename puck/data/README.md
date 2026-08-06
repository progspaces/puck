## Data

Data contains 4 folders which after running the .py files from image_annotations, are expected to remain static/immutable throughout the rest of the experiments.
It is here that the ground truth and raw data of images we will test our different approaches on stay nice and untouched.

images_copy and images_miniset follow the pattern of palette>location>height>permutation as that's how they were gathered in images_annotation.
However images_calibration is structured as height>palette>location as those images were taken later and i found it significantly more convenient to stay in one location, change palette, and then change height.

