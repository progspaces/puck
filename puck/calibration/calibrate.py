from dataclasses import dataclass
import logging
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray
from screeninfo import Monitor, get_monitors

from .chessboard import make_chessboard


# each file should have it's own logger
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Calibration Information
# -----------------------------------------------------------------------------


@dataclass
class CalibrationInfo:
    """
    A container for any and all results of the calibration process.
    This class can be saved after calibration and loaded at the the
    start of future sessions.
    """

    camera_to_projector_homography: np.ndarray

    def save(self, path: Path) -> None:
        np.savetxt(path, self.camera_to_projector_homography)

    @classmethod
    def load(cls, path: Path) -> "CalibrationInfo":
        mat = np.loadtxt(path)
        return CalibrationInfo(camera_to_projector_homography=mat)


# -----------------------------------------------------------------------------
# Helper functions - projector
# -----------------------------------------------------------------------------


def log_monitors_info() -> None:
    """
    Use the screeninfo package to print the current monitors.
    Useful for debugging
    """
    monitors = get_monitors()
    for idx, m in enumerate(monitors):
        info = f"Monitor {idx}. w:{m.width}, h:{m.height}, x:{m.x}, y:{m.y}."
        logger.info(info)


def get_projector(id: int) -> Monitor:
    """
    Get information about the projector.

    Args:
        id (int): The id of the projector (normally 0 or 1).

    Returns:
        Monitor: A screeninfo Monitor object with info about the projector.
    """
    monitors = get_monitors()
    return monitors[id]


def create_fullscreen_window(window_name: str, monitor: Monitor) -> None:
    """
    Reliably create a fullscreen window on the given monitor,

    Args:
        window_name (str): The name to give the window so you can draw to it.
        monitor (Monitor): The information about the monitor.
    """
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, monitor.x, monitor.y)
    cv2.resizeWindow(window_name, monitor.width, monitor.height)

    # opencv does not create native windows until the first image is shown
    screen_shape = (monitor.height, monitor.width, 3)
    screen_sized_image = np.zeros(screen_shape, np.uint8)
    cv2.imshow(window_name, screen_sized_image)
    cv2.waitKey(100)  # give it a moment to create the native window

    # full screen the window
    cv2.moveWindow(window_name, monitor.x, monitor.y)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Refresh after changing the native window style. Some backends otherwise
    # defer fullscreen until the next frame is rendered.
    cv2.imshow(window_name, screen_sized_image)
    cv2.waitKey(100)  # give it a moment to create the native window


# -----------------------------------------------------------------------------
# Helper functions - camera
# -----------------------------------------------------------------------------


def read_frames(
    camera: cv2.VideoCapture,
    count: int = 5,
) -> list[NDArray[np.uint8]]:
    """Read count frames from the camera.

    Args:
        camera (cv2.VideoCapture): The camera.
        count (int, optional): The number of frames to drop. Defaults to 5.

    Raises:
        RuntimeError: The camera might fail (unplugged etc).
    """
    frames: list[NDArray[np.uint8]] = []
    for _ in range(count):
        ok, frame = camera.read()

        if not ok:
            raise RuntimeError("Could not read camera frame")

        frames.append(frame)
    return frames


def capture_average(
    camera: cv2.VideoCapture,
    count: int = 5,
) -> NDArray[np.uint8]:
    frames = read_frames(camera, count)
    frames = [frame.astype(np.float32) for frame in frames]
    average = np.mean(frames, axis=0)
    return average.astype(np.uint8)


# -----------------------------------------------------------------------------
# Exported functionality
# -----------------------------------------------------------------------------
def calibrate(projector_id: int, camera_id: int) -> CalibrationInfo:
    logger.info("Calibrating system ...")

    PROJECTOR_WINDOW_NAME = "projector"

    # get the projector information
    projector = get_projector(projector_id)

    # generate the chessboard
    board_size = (projector.width, projector.height)
    board_image, board_points = make_chessboard(board_size)

    # create a fullscreen window for the projector to draw to
    create_fullscreen_window(PROJECTOR_WINDOW_NAME, projector)

    try:
        # set up the camera
        camera = cv2.VideoCapture(camera_id)
        if not camera.isOpened():
            raise RuntimeError("Calibration Error: cannot open camera")

        # capture the background
        read_frames(camera, count=5)  # discard 5 frames
        background_frame = capture_average(camera, count=10)

        # project the chessboard
        cv2.imshow(PROJECTOR_WINDOW_NAME, board_image)
        cv2.waitKey(100)

        # capture the chessboard
        read_frames(camera, count=5)  # discard 5 frames
        chessboard_frame = capture_average(camera, count=10)

        # compute the grayscale difference image
        gray_background = cv2.cvtColor(background_frame, cv2.COLOR_BGR2GRAY)
        gray_chessboard = cv2.cvtColor(chessboard_frame, cv2.COLOR_BGR2GRAY)
        difference = cv2.subtract(gray_chessboard, gray_background)

        # normalise the difference image then OTSU threshold
        # norm makes for better OTSU threshold
        difference = cv2.normalize(
            difference, None, alpha=0, beta=0, norm_type=cv2.NORM_MINMAX
        )
        thesh, mask = cv2.threshold(
            difference, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )

        # now we have the mask, we can detect the chessboard
        # note - we could fallback to the non-thesholded image it that fails
        corner_shape = (
            board_shape[0] - 1,
            board_shape[1] - 1,
        )
        detector_flags = (
            cv2.CALIB_CB_NORMALIZE_IMAGE
            | cv2.CALIB_CB_EXHAUSTIVE
            | cv2.CALIB_CB_ACCURACY
        )
        found, corners = cv2.findChessboardCornersSB(
            detector_image,
            corner_shape,
            flags=detector_flags,
        )

        # if we can't find the chessboard then raise an exception
        if not found:
            raise RuntimeError("Cannot find chessboard!")

        # compute the mapping from the camera-image coords to the projector coords
        # both arrays need to be row-major order https://en.wikipedia.org/wiki/Row-_and_column-major_order
        # e.g. [[x1,y1],[x2,y2]]
        # the chessboard is symmetric under 180-degree rotation and the detector may return
        # the corners in reverse order
        camera_points = corners.reshape(-1, 2).astype(np.flaot32)
        if camera_points[0].sum() > camera_points[-1].sum():
            camera_points = camera_points[::-1].copy()

        projector_points = np.asarray(board_points, dtype=np.float32)
        homography, inlier_mask = cv2.findHomography(
            camera_points,
            projector_points,
            method=cv2.RANSAC,
            ransacReprojThreshold=5.0,
        )

        if homography is None or inlier_mask is None:
            raise RuntimeError(
                "Could not compute the camera-to-projector homography matrix."
            )

    finally:
        camera.release()
        cv2.destroyAllWindows()

    return CalibrationInfo(camera_to_projector_homography=homography)
