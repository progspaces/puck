# Puck Directory

The directory has 6 folders, analysis, code_modules, data, experiments, image_annotation, and output.

Data contains all the raw image files taken from the webcam, seperated into:
    annotations, the .json files of our annotations amongst the three annotators of the mini-set as well as the annotations of the full dataset.
    image_calibration, all the calibration images
    images_copy, the webcam images with personally identifiable information edited out. the original dataset was named images, and images_copy helped differentiate which set had been edited and which hadn't.
    images_miniset, the subset of the image data set that all three annotators annotated.
That folder's data is tied to the image_annotation folder which contains the python files that take the webcam photos, start a new annotator's annotation run, as well as calculate the interannotator agreement

Code_modules contain the core python files broken into folders of applications, such as calibration, dot_finding, permutation_guessing etc.
All of these files are saved as their own code modules and thus can be called on in other python files, most typically the experimental files. Functions originate in these folders, and then are used in the experiment files to test ideas and get back results. On their own, they do not run as stand alone python files, but as little libraries for their goals.

Experiments contains folders and python files that test best thresholding methods, best timing methods, and other measures of sucess, and utilize the code modules python functions almost exclusively.
They also often call into the data folder to check with the anntoations as ground truth and the raw image data as test sets. Their outputs tend to go to the output folder, which stores the results of these experiments.
Experiments can also be called from the CLI as they all are wrapped up in main() functions.

Finally analysis contains Jupyter notebooks that analyze the results of the experiments. You can adjust them to find pre-existing output files based on your own file directory, but for conveinece sake, the exepriments can also be run in their own cells and return the paths or a dictionary of the paths in which their output is stored. This is most convinent for running quick visualizations and getting fast insight into how the experiments are running rather than trying to run everything out of just plain .py files. 

