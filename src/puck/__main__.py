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

# Local packages and modules
from .geometry import Point, Polygon, ordered_rectangle
from .actor import Actor
from .calibration import calibrate

# Global variables
logger = logging.getLogger(__name__)
DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
CANVAS_HEIGHT, CANVAS_WIDTH = 1080, 1920
CAMERA_PERSPECTIVE_WINDOW_NAME = "Camera perspective"


def logging_setup(log: bool, log_level: int) -> None:
    """Sets up the logging object and the level at which we are logging for different approaches, info vs debug.

    Args:
        log (bool): To log or not to log that is the question. (Turns on logging)
        log_level (int): Level of logging you wish to have outputted.
    """
    if log:
        logging.basicConfig(level=log_level)
        logger.info(f"Logging working at level {log_level}")


def tk_setup() -> None:
    """Sets up the tkinter window where it will draw graphics.
    """
    base.tk.call("tk", "scaling", 2.0)
    base.title("Tkinter Widget Size")
    base.wm_attributes("-fullscreen", True)

    # Assume 1080p double-monitor setup.
    base.geometry("1920x1080+0+-1080")


def load_program_store(filename: str) -> dict[str, str]:
    """Loads in a .json dictionary for looking up what string is associated with what program name

    Args:
        filename (str): the file name of the .json dictionary

    Returns:
        dict[str, str]: the dictionary loaded as a dicionary object.
    """
    with open(filename) as f:
        return dict(json.load(f))


def canvas_setup(base: Tk) -> Canvas:
    """Set up the tk canvas object on the tk base object.

    Args:
        base (Tk): The basic Tk object that everything is built off of

    Returns:
        Canvas: A tk canvas on which we can draw graphical objects.
    """
    canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black") # Creation.
    canvas.pack() # Laying it out.
    return canvas


def camera_setup(camera_id: int) -> cv.VideoCapture:
    """Set up your camera to get a videofeed input.

    Args:
        camera_id (int): camera id, typically 0 or 1

    Returns:
        cv.VideoCapture: video feed
    """
    # Create camera
    cam = cv.VideoCapture(camera_id)

    # Get one frame to verify (will throw if broken)
    _, frame = cam.read()
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    return cam


def camera_perspective_window_setup(window_name: str):
    """Set up a window that will show you what the camera is seeing. 
    Oddly here the name of the window will be used to refer to it later on so it acts 
    less like a random tidbit on the cv window and closer to an identifier.

    Args:
        window_name (str): Name of the window that shows up.
    """
    cv.namedWindow(
        window_name,
        cv.WINDOW_FREERATIO,
    )
    cv.moveWindow(window_name, 0, 300)
    cv.resizeWindow(window_name, 600, 500)


def average_pt(tag: Polygon) -> Point:
    """Takes the AprilTag shape and finds the middle point."""
    sum_x = 0
    sum_y = 0
    for x, y in tag:
        sum_x += x
        sum_y += y
    return Point(int(sum_x / 4), int(sum_y / 4))


def detect_paper_tags(frame: np.array) -> list[tuple[Polygon, list[int]]]:  
    """Takes in a frame of the video and determines what papers are wtihin it.
    Currently we are just looking for one paper at a time, this needs to be increased in newer implementations.

    Args:
        frame (np.array): a frame of the video feed.

    Returns:
        A list of papers and their associated list of four tags
    """
    detector = cv.aruco.ArucoDetector(dictionary=DICT) # Create a cv detector to find the appropriate Apriltags
    tags, ids, _ = detector.detectMarkers(frame) # Return the corners and ids found in the image.
    tag_shapes = [Polygon.from_array(tag[0]) for tag in tags]
    if ids is not None and len(ids) == 4: # If there are ids, and only 4 of them then ->
        bads = [x for x in ids if x > 4] # If any of the ids are greater than 4, then we cannot do a base 4 transformation we have misrecognized an AprilTag
        if len(bads) > 0: # There are ids that we shouldn't be recognizing so we should take down the problematic frame
            ## SAVE WHERE IT SEES THE BAD THING
            copy = cv.aruco.drawDetectedMarkers(frame, tags, ids)
            plt.figimage = copy
            plt.savefig("problematic_frame.png")  # we could come up with a better name for it, but if this shows up in your file system at least you know something has gone wrong.
        averaged_paper = Polygon([ average_pt(shape) for shape in tag_shapes])
        return [(averaged_paper, ids)] # Currently only returns one entry in the list, this should be many tuples in an updated implementation.
    else:
        return []


def tags_to_pid(tags: list[int]) -> int | None:
    """Takes in all the scene apriltags and transforms them into a single integer which is the id of the paper.

    Args:
        tags list[int]: a list of the ids given

    Returns:
        int: the program encoding as an integer, if this is supposed to be 3, it returns 3.
    """
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
    current_coords: Polygon,
    encoding_to_actor: dict[str, Actor],
    program_lookup: dict[str, str],
    drawing_queue: Queue,
) -> None:
    """Takes in a program encoding and the coordinates of the paper associated with it and creates actors 

    Args:
        program_encoding (int): the program identifier
        current_coords (Polygon): a list of the coordinates of the paper.
        encoding_to_actor (dict[str, Actor]): a dictionary storing the encoding of the program (int as str) to the actor it starts
        program_lookup (dict[str, str]): a dictionary storing the encoding of the program (int as a str) to the program name
        drawing_queue (Queue): a universal queue that can only be used by the main thread to create graphics objects
    """
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
    """Draws what is on the drawing queue onto the canvas.

    Args:
        drawing_queue (Queue): the queue that all the actors and main thread can access
        canvas (Canvas): the tkinter graphical space.
    """
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
                            coordinates.unwrap(), fill=fill, outline=outline, width=width
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
                        canvas.coords(id, coordinates.unwrap())
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
    """Update the system with input from the camera.
    Recursively adds itself onto the event loop for base.mainloop() using the .after() call.

    Args:
        cam (cv.VideoCapture): videofeed
        encoding_to_actor (dict[str, Actor]): a dictionary tying the program encoding to the actor that it spawns
        program_lookup (dict[str, str]): a dictionary tying the program encoding (int as a str) to the name of the program it is assocaited with.
        drawing_queue (Queue): the universal drawing queue that all actors and the main thread can access
        canvas (Canvas): the tkinter canvas
        window_name (str): the name of the window that shows the camera feed
    """
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
            coords =  ordered_rectangle(coords, coords[0])
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


def start_puck(log: bool = False, log_level: int = 0, camera_id: int = 0, program_lookup_file: str = "data/program_lookup.json") -> None:
    """Runs the puck recognition system

    Args:
        log (bool, optional): Whether or not you are logging information about this run. Defaults to False.
        log_level (int, optional): If you are logging at what level of detail are you logging information. Defaults to 0.
        camera_id (int, optional): The id of the camera that is looking at the scene. Defaults to 0.
    """
    print("Hello from puck!") ## Generic print to make sure that everything is working
    logging_setup(log, log_level) ## Setup the logger using the command line arguments
    # calibration_info = calibrate(projector_id=0, camera_id=0) ## Returns homology matrix
    # calibration_info.camera_to_projector_homography # To deal with later
    tk_setup() ## Set up the tkinter windows 
    program_lookup = load_program_store(program_lookup_file) # Load the dictionary of programs 
    encoding_to_actor: dict[str, Actor] = {} # Create an empty dictionary of strings to actors (probably will update to integer to Actor)
    canvas = canvas_setup(base) # Set up the canvas using 'base' a global tkinter variable set up at the beginning, required for all graphical commands in this implementation 
    drawing_queue: Queue = Queue() # Drawing queue created here so that all actors can access it as well as the main thread.
    cam = camera_setup(camera_id) # Cv2 camera set up so that we can get input from the real physical scene.
    camera_perspective_window_setup(CAMERA_PERSPECTIVE_WINDOW_NAME) # using that camera to create a window that shows us what the camera is seeing.
    base.after(
        16,
        update,
        cam,
        encoding_to_actor,
        program_lookup,
        drawing_queue,
        canvas,
        CAMERA_PERSPECTIVE_WINDOW_NAME,
    ) # Add a call to 'update' onto the base event loop with the arguments (cam, encoding_to_actor,program_lookup,drawing_queue, canvas, CAMERA_PERSPECTIVE_WINDOW_NAME,)
    base.mainloop() # Start the event loop, it will hang out here until stopping condition is met.
    cam.release() # Get rid of the camera.
    cv.destroyAllWindows() # destroy all cv windows.


def main() -> None:
    """Runs the 'start_puck' function, wrapped up in typer.run so it can act as a command line tool and take in command arguments.
    """
    typer.run(start_puck)
