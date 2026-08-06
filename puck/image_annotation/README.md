## Image Annotation

The image annotation folder contains all the .py files to get images from the webcam, annotate them and calculate the inter-annotator reliability scores.
Its output is the data folder.

annotator.py holds the basic function to annnotate all files, and is called by massAnnotations.py and miniAnnotations.py
massAnnotations.py was used by a singular annotator to annotate all the images in the dataset and created a .json file for all the results as well as saved "_annotated" .jpgs with their information visually overlaid on top of the images.
miniAnnotations.py can be used by anyone to create their own annotations for the subset of images that end with 0.jpg. This reduced the overall annotation workload and provided alternative annotations for those images. Their output also goes into data as a .json file. The overlaid images may or may not be saved depending on the users preferences, but is largely considered unncessary unless some drastic bug occurs.

next krippendorff_alpha.py is used as a small library of functions for calculating the inter-annotator reliability between annotators. it is called in the experiment, annotator_reliability.py

finally, webcamFeed.py is used to collect the images in the first place and prompts the user to take a photo at each of the predesignated locations and heights 5 times. It is entirely a CLI file and only used in the intial gathering of data so is not called in any experiments or analysis notebooks. 