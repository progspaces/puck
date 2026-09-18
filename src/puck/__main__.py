# Setup tkinter early (necessary on MacOS).
from tkinter import * # TODO: avoid *
base = Tk()

# Other imports
import logging
import typer

# Global variables
logger = logging.getLogger(__name__)

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


def start_puck(log: bool = False, log_level: int = 0) -> None:
    print("Hello from puck!")
    logging_setup(log, log_level)
    tk_setup()


def main() -> None:
    typer.run(start_puck)
