# Setup tkinter early (necessary on MacOS).
from tkinter import *  # TODO: avoid *

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

# Local packages and modules
from . import geometry
from .actor import Actor

# Global variables
logger = logging.getLogger(__name__)
PROGRAM_LOOKUP_FILE = "data/program_lookup.json"  # TODO: make configurable
DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
CANVAS_HEIGHT, CANVAS_WIDTH = 1080, 1920
CAMERA_PERSPECTIVE_WINDOW_NAME = "Camera perspective"


def logging_setup(log: bool, log_level: int) -> None:
    if log:
        logging.basicConfig(level=log_level)
        logger.info(f"Logging working at level {log_level}")


def tk_setup() -> None:
    base.tk.call("tk", "scaling", 2.0)
    base.title("Tkinter Widget Size")
    base.wm_attributes("-fullscreen", True)

    # Assume 1080p double-monitor setup.
    base.geometry("1920x1080+0+-1080")


def load_program_store(filename: str) -> dict[str, str]:
    with open(filename) as f:
        return dict(json.load(f))


def canvas_setup(base: Tk) -> Canvas:
    canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black")
    canvas.pack()
    return canvas


def camera_setup(camera_id: int) -> cv.VideoCapture:
    # Create camera
    cam = cv.VideoCapture(camera_id)

    # Get one frame to verify (will throw if broken)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    return cam


def camera_perspective_window_setup(window_name: str):
    cv.namedWindow(
        window_name,
        cv.WINDOW_FREERATIO,
    )
    cv.moveWindow(window_name, 0, 300)
    cv.resizeWindow(window_name, 600, 500)


def average_pt(corners: list[tuple[int, int]]) -> tuple[int, int]:
    sum_x = 0
    sum_y = 0
    for pair in corners:
        sum_x += pair[0]
        sum_y += pair[1]
    return (int(sum_x / 4), int(sum_y / 4))


def detect_paper_tags(
    frame: np.array,
) -> list[
    tuple[list[tuple[int, int]], list[int]]
]:  # TODO: sort out this type nightmare
    input = frame
    detector = cv.aruco.ArucoDetector(dictionary=DICT)
    corners, ids, _ = detector.detectMarkers(input)
    if ids is not None and len(ids) == 4:
        bads = [x for x in ids if x > 4]
        if len(bads) > 0:
            ## SAVE WHERE IT SEES THE BAD THING
            copy = cv.aruco.drawDetectedMarkers(input, corners, ids)
            plt.figimage = copy
            plt.savefig("test.png")  ##??
        corners_a = corners[0][0]
        corners_b = corners[1][0]
        corners_c = corners[2][0]
        corners_d = corners[3][0]
        averaged_paper = [
            average_pt(corners_a),
            average_pt(corners_b),
            average_pt(corners_d),
            average_pt(corners_c),
        ]
        return [(averaged_paper, ids)]
    else:
        return []


def tags_to_pid(tags):
    if tags is not None:
        filtered = [id for id in tags if id < 5][0:5]
        program_encoding = int("".join(map(str, filtered)), 4)
        if program_encoding == 192 or program_encoding == 48 or program_encoding == 12:
            program_encoding = 3
        logger.debug(f"Raw id: {tags} to interpreted id: {program_encoding}")
        return program_encoding
    else:
        return None


def create_and_update_actors(
    program_encoding: int,
    current_coords: list[tuple[int, int]],
    encoding_to_actor: dict[str, Actor],
    program_lookup: dict[str, str],
    drawing_queue: Queue,
) -> None:
    # TODO: program_encoding should have ints, not strs in the json file
    if str(program_encoding) not in program_lookup:
        print(f"There is no associated program with the encoding: {program_encoding}")
        return

    # TODO: use this to load modules dynamically
    module_name = "puck.programs." + program_lookup[str(program_encoding)]
    module = importlib.import_module(module_name)

    if t := encoding_to_actor.get(str(program_encoding)):
        # This program is already running
        # TODO: the id isn't used at the moment
        t.send(("update_shape", ("id", 0), ("coordinates", current_coords)))
    else:
        # This program is not yet running
        t = Actor(target=module.run)
        encoding_to_actor[str(program_encoding)] = t
        t.start()
        # TODO: pass as environment on construction instead
        t.send(("drawing_queue", drawing_queue))
        t.send(("new_shape", ("type", "rectangle"), ("coordinates", current_coords)))


def draw(drawing_queue: Queue, canvas: Canvas) -> None:
    if not drawing_queue.empty():  # TODO: change to 'while'
        message = drawing_queue.get()
        logger.debug(f"draw loop got message {message}")

        assert message != "kill"
        match message:
            case (
                "action",
                _ as action,
            ):
                match action:
                    case (
                        "new",
                        ("type", type),
                        ("sender", sender),
                        ("coordinates", coordinates),
                    ):
                        assert type == "rectangle" or type == "polygon"
                        outline = "blue"
                        fill = "white"
                        width = 2
                        id = canvas.create_polygon(
                            coordinates, fill=fill, outline=outline, width=width
                        )
                        sender.send(("information", ("add_ids", [id])))
                    case ("new", *invalid_new):
                        print(
                            f"You have provided me this message, {invalid_new},"
                            "to create a new graphical object, but I'm not sure what type of object. \n "
                            "It would help if you specified the type of object you want to add."
                        )
                    case (
                        "update",
                        ("id", id),
                        ("coordinates", coordinates),
                        *further_info,
                    ):
                        canvas.coords(id, coordinates)
                    case _ as invalid_action:
                        print(
                            f"You have provided an invalid action message, '{invalid_action}' is not an action I understand"
                        )
            case _ as invalid_message:
                print(
                    f"You have provided an invalid message, '{invalid_message}' is not a message I understand"
                )
        logger.debug("drawing loop finished")
    canvas.pack()


def update(
    cam: cv.VideoCapture,
    encoding_to_actor: dict[str, Actor],
    program_lookup: dict[str, str],
    drawing_queue: Queue,
    canvas: Canvas,
    window_name: str,
) -> None:
    logger.debug("Called the Update Function")

    # Get a frame
    _, frame = cam.read()
    cv.imshow(window_name, frame)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Recognise and execute papers
    for coords, tags in detect_paper_tags(frame):
        program_encoding = tags_to_pid(tags)
        if program_encoding:
            logger.debug(f"Saw program encoding, {program_encoding}")
            coords =  geometry.ordered_rectangle(coords, coords[0])
            create_and_update_actors(
                program_encoding,
                coords,
                encoding_to_actor,
                program_lookup,
                drawing_queue,
            )

    draw(drawing_queue, canvas)

    # Handle quitting
    if cv.waitKey(1) == ord("q"):
        logger.info("In the stopping condition")
        for encoding, a in encoding_to_actor.items():
            a.end()
            logger.info(f"encoding asscoiated is : {encoding}")
            logger.info("Got past the end, onto Join now")
            a.join()
        logger.info("finished the joining and ending")
        base.quit()

    # Tell event loop to run this again in 16ms
    base.after(
        16,
        update,
        cam,
        encoding_to_actor,
        program_lookup,
        drawing_queue,
        canvas,
        window_name,
    )


def start_puck(log: bool = False, log_level: int = 0, camera_id: int = 0) -> None:
    print("Hello from puck!")
    logging_setup(log, log_level)
    tk_setup()
    program_lookup = load_program_store(PROGRAM_LOOKUP_FILE)
    encoding_to_actor: dict[str, Actor] = {}
    canvas = canvas_setup(base)
    drawing_queue: Queue = Queue()
    cam = camera_setup(camera_id)
    camera_perspective_window_setup(CAMERA_PERSPECTIVE_WINDOW_NAME)
    base.after(
        16,
        update,
        cam,
        encoding_to_actor,
        program_lookup,
        drawing_queue,
        canvas,
        CAMERA_PERSPECTIVE_WINDOW_NAME,
    )
    base.mainloop()
    cam.release()
    cv.destroyAllWindows()


def main() -> None:
    typer.run(start_puck)
