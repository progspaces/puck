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

from .calibration import calibrate

# Global variables
logger = logging.getLogger(__name__)

calibration_info = calibrate(projector_id=0, camera_id=0)
