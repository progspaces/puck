# Setup tkinter early (necessary on MacOS).
from tkinter import * # TODO: avoid *
base = Tk()

# Standard packages
import logging

# External packages
import typer

# Local packages and modules
from actor import Actor

# Global variables
logger = logging.getLogger(__name__)
PROGRAM_LOOKUP_FILE = 'puck/program_store/program_lookup.json' # TODO
DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)

def logging_setup(log: bool, log_level: int) -> None:
    if log:
        logging.basicConfig(level=log_level)
        logger.log(level=logging.INFO, msg= f"Logging working at level {log_level}")


def tk_setup() -> None:
    base.tk.call('tk', 'scaling', 2.0)
    base.title('Tkinter Widget Size')
    base.wm_attributes("-fullscreen", True)

    # Assume 1080p double-monitor setup.
    base.geometry("1920x1080+0+-1080")


def load_program_store(filename: str) -> dict[str, str]:
    with open(filename) as f:
        return dict(load(f))


def start_puck(log: bool = False, log_level: int = 0) -> None:
    print("Hello from puck!")
    logging_setup(log, log_level)
    tk_setup()
    program_lookup = load_program_store(PROGRAM_LOOKUP_FILE)
    encoding_to_actor: dict[str, Actor] = {}


def main() -> None:
    typer.run(start_puck)
