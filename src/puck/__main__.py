# Setup tkinter early (necessary on MacOS).
from tkinter import * # TODO: avoid *
base = Tk()

# Standard packages
import logging

# External packages
import cv2 as cv
import typer

# Local packages and modules
from actor import Actor

# Global variables
logger = logging.getLogger(__name__)
PROGRAM_LOOKUP_FILE = 'puck/program_store/program_lookup.json' # TODO
DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
C_HEIGHT, C_WIDTH = 1080, 1920
CAMERA_PERSPECTIVE_WINDOW_NAME = "Camera perspective"

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


def canvas_setup(base: Tk) -> Canvas:
    canvas = Canvas(base, height=C_HEIGHT, width=C_WIDTH, background='black')
    canvas.pack()
    return canvas

def camera_setup() -> cv.VideoCapture:
    # Create camera
    cam = cv.VideoCapture(0)

    # Get one frame to verify (will throw if broken)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    return cam


def camera_perspective_window_setup(window_name: str):
    cv.namedWindow(window_name, cv.WINDOW_FREERATIO,)
    cv.moveWindow(window_name, 0, 300)
    cv.resizeWindow(window_name, 600, 500)


def detect_paper_tags(frame: np.array) -> list[tuple[list[tuple[int, int]], list[int]]]:  # TODO: sort out this type nightmare
    input = frame
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    if ids is not None and len(ids)==4:
        bads = [x for x in ids if x>4]
        if len(bads) >0 :
                ## SAVE WHERE IT SEES THE BAD THING
                copy = cv.aruco.drawDetectedMarkers(input, corners, ids)
                plt.figimage = copy
                plt.savefig('test.png') ##??
        corners_a = corners[0][0]
        corners_b = corners[1][0]
        corners_c = corners[2][0]
        corners_d = corners[3][0]
        averaged_paper = [average_pt(corners_a),
                          average_pt(corners_b),
                          average_pt(corners_d),
                          average_pt(corners_c)]
        return [(averaged_paper, ids)]
    else:
        return [(None,None)]


def tags_to_pid(tags):
    if tags is not None:
        filtered = [id for id in tags if id <5][0:5]
        program_encoding = int("".join(map(str, filtered)),4)
        if program_encoding == 192 or program_encoding == 48 or program_encoding == 12:
            program_encoding = 3
        logger.log(level = 16, msg = f"Raw id: {tags} to interpreted id: {program_encoding}")
        return program_encoding
    else:
        return None


def update(cam: cv.VideoCapture, window_name: str) -> None:
    logger.log(level=19, msg="Called the Update Function")

    # Get a frame
    _, frame = cam.read()
    cv.imshow(window_name, frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Recognise and execute papers
    for coords, tags in detect_paper_tags(frame):
        program_encoding = tags_to_pid(tags)
        logger.log(level = 18, msg = f"Saw program encoding, {program_encoding}")
        coords = order_coordinates_to_avoid_x(coords=coords)
        handle_currently_recognized(program_encoding, coords, drawing_queue)

    draw_loop(drawing_queue=drawing_queue, canvas= canvas)
    if cv.waitKey(1) == ord('q'): ## stopping condition
        logger.log(level = 17, msg = f"In the stopping condition")
        for encoding,a in encoding_to_actor.items():
            a.end()
            logger.log(level = 16, msg = f"encoding asscoiated is : {encoding}")
            logger.log(level = 16, msg = "Got past the end, onto Join now")
            a.join()
        logger.log(level = 17, msg = f"finished the joining and ending")
        logger.log(level = 17, msg = f"The initial number of objects in the canvas was {initial_number}" )
        logger.log(level = 17, msg = f"The number of objects in the canvas is {len(canvas.find_all())}" )
        base.quit()
    base.after(16, update, cam)  # Timed Check, adding itself back onto the queue to run 20ms later


def start_puck(log: bool = False, log_level: int = 0) -> None:
    print("Hello from puck!")
    logging_setup(log, log_level)
    tk_setup()
    program_lookup = load_program_store(PROGRAM_LOOKUP_FILE)
    encoding_to_actor: dict[str, Actor] = {}
    canvas = canvas_setup(base)
    drawing_queue = Queue()
    cam = camera_setup()
    camera_perspective_window_setup(CAMERA_PERSPECTIVE_WINDOW_NAME)



def main() -> None:
    typer.run(start_puck)
