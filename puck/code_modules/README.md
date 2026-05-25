## code_modules

This folder contains what I like to think of as little libraries or little python packages that each address a specific goal.

calibration addresses the calibration images and using them to create a ground truth of colors that are detected by the webcam, it relies on the geometry module.

colour_conversion contains colour_conversion.py which holds functions that convert between the luv, rgb, cmyk, and hsv colour spaces, these are much less used than they were intially when trying to figure out what colour space provided the best results when trying to decide what colour a dot was. colour_finding.py is used to find the black dot in the calibration square and return the colours and coordinates of the existing dots. It relies a bit on the colour_conversion.py functions to move through colour spaces, though many of the if-else branches are not used in the pipeline currently they remain in the function incase a switch between colour spaces would be beneficial in the future.

dot_finding contains dot_finder.py which has the two most promising dot detection methdos, a stepwise iterative method and a hough circle transform that is well parameterized for these cases. Currently we use the hough circle transform, but the iterative approach could also work, just slower if something goes wrong with the hough approach.

geometry contains clockwise_dots.py, rectangles.py, and squares.y which finds the clockwise dot in a rectangle relative to a starting dot, determines if there are any rectangles formed by a list of given key points and determines how many of those are squares. these are all utilized heavily by the calibration module and permutation_guessing.py experiment.

helper_functions contains the computational_time file created by the Drs. Harris-Birtill as well as various helper functions such as clamp that did not fit anywerhe else.

