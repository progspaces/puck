# saved_cal = ""

# try:
#     cal = load(saved_cal)
# except OSError:
#     calibration_info = calibrate()
#     calibration_info.save(camera_calibration)

# Setup tkinter early (necessary on MacOS).
from tkinter import Tk, Canvas, NW


from PIL import ImageTk, Image
base = Tk()
import cv2 as cv
from puck.calibration.calibration import make_camera_to_real,project_chessboard
from puck.camera_processor import camera_setup
from puck.offset import offset_string,size_of_second

CANVAS_HEIGHT, CANVAS_WIDTH = size_of_second()

def tk_setup() -> None:
    """Sets up the tkinter window where it will draw graphics."""
    # base.tk.call("tk", "scaling", 2.0)
    base.title("Tkinter Widget Size")
    # base.wm_attributes("-fullscreen", True)

    # Assume 1080p double-monitor setup.
    base.geometry(offset_string()) 


def canvas_setup(base: Tk) -> Canvas:
    """Set up a Tk.Canvas object on the base object.

    Args:
        base: an instance of Tk(), also commonly referred to as "root".
    """
    canvas = Canvas(
        base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black"
    )

    # Allows canvas to be seen by the user.
    canvas.pack()
    return canvas



def main():
    tk_setup()        
    canvas = canvas_setup(base)
    project_chessboard(canvas)
    base.mainloop()
    print("end")

main()