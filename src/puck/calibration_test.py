# Setup tkinter early (necessary on MacOS).
from tkinter import Tk, Canvas

base = Tk()

# Standard packages
import importlib
import json
import logging
from queue import Queue

# External packages
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import typer

from calibration import calibrate

# Global variables
logger = logging.getLogger(__name__)




def logging_setup(log: bool, log_level: int) -> None:
    """Sets up the logging object and the level at which we are logging for different approaches, info vs debug.

    Args:
        log (bool): To log or not to log that is the question. (Turns on logging)
        log_level (int): Level of logging you wish to have outputted.
    """
    if log:
        logging.basicConfig(level=log_level)
        logger.info(f"Logging working at level {log_level}")

def run_calibration(log: bool = False, log_level: int = 0,):
    print("Hello from calibration!") ## Generic print to make sure that everything is working
    logging_setup(log, log_level) ## Setup the logger using the command line arguments
    calibration_info = calibrate(projector_id=0, camera_id=0)
    print(calibration_info.camera_to_projector_homography)

def main() -> None:
    typer.run(run_calibration)

main()