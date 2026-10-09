from collections import deque
import logging

import cv2
import numpy as np
from numpy.typing import NDArray

from puck.calibration import calibrate

logger = logging.getLogger(__name__)

WINDOW_CONTOURS = "contours"
WINDOW_FOREGROUND = "foreground mask"


def detect_objects(
    frame: NDArray[np.uint8],
    background_frame: NDArray[np.uint8],
    projector_bounds: NDArray[np.float32],
    minimum_area: int = 300,
    minimum_fill_ratio: float = 0.2,
    maximum_aspect_ratio: float = 5.0,
    foreground_history: deque[NDArray[np.uint8]] | None = None,
):
    """Segment foreground objects inside the camera-visible projector area."""
    if frame.shape != background_frame.shape:
        raise ValueError(
            "Frame and calibration background must have matching shapes"
        )

    foreground = cv2.absdiff(frame, background_frame)
    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    automatic_threshold, _ = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU,
    )

    threshold_value = max(10.0, automatic_threshold * 0.5)
    _, foreground_mask = cv2.threshold(
        blurred,
        threshold_value,
        255,
        cv2.THRESH_BINARY,
    )

    projector_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(
        projector_mask,
        np.rint(projector_bounds).astype(np.int32),
        255,
    )

    projector_mask = cv2.erode(
        projector_mask,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)),
    )
    foreground_mask = cv2.bitwise_and(foreground_mask, projector_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    foreground_mask = cv2.morphologyEx(
        foreground_mask,
        cv2.MORPH_OPEN,
        kernel,
    )
    foreground_mask = cv2.morphologyEx(
        foreground_mask,
        cv2.MORPH_CLOSE,
        kernel,
    )

    if foreground_history is not None:
        foreground_history.append(foreground_mask.copy())
        foreground_mask = np.where(
            np.mean(np.stack(foreground_history), axis=0) >= 127.5,
            255,
            0,
        ).astype(np.uint8)

    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        foreground_mask
    )
    contours: list[NDArray[np.int32]] = []
    for label in range(1, component_count):
        area = stats[label, cv2.CC_STAT_AREA]
        width = stats[label, cv2.CC_STAT_WIDTH]
        height = stats[label, cv2.CC_STAT_HEIGHT]
        fill_ratio = area / (width * height)
        aspect_ratio = max(width, height) / max(1, min(width, height))
        if (
            area < minimum_area
            or fill_ratio < minimum_fill_ratio
            or aspect_ratio > maximum_aspect_ratio
        ):
            continue
        component_mask = np.where(labels == label, 255, 0).astype(np.uint8)
        component_contours, _ = cv2.findContours(
            component_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        if component_contours:
            contours.append(max(component_contours, key=cv2.contourArea))

    return contours, foreground_mask


def get_camera_space_projector_bounds(
    camera_calibration: calibrate.CalibrationInfo,
    projector_size: tuple[int, int],
) -> NDArray[np.float32]:
    """Return the projector's four corners in camera-image coordinates."""
    width, height = projector_size
    projector_corners = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=np.float32,
    ).reshape(-1, 1, 2)
    projector_to_camera = np.linalg.inv(
        camera_calibration.camera_to_projector_homography
    )
    return cv2.perspectiveTransform(
        projector_corners,
        projector_to_camera,
    ).reshape(-1, 2)


def get_projector_space_object_bounds(
    contours: list[NDArray[np.int32]],
    camera_calibration: calibrate.CalibrationInfo,
) -> list[NDArray[np.float32]]:
    """Change the contours into the projector space"""
    homography = camera_calibration.camera_to_projector_homography
    if homography is None:
        raise ValueError("Camera calibration has no homography")

    bounds: list[NDArray[np.float32]] = []
    for contour in contours:
        print("contours")
        print(contour)
        print(contour.astype(np.float32))
        print("shapes")
        print(contour.shape)
        print(homography.shape)
        projector_contour = cv2.perspectiveTransform(
            contour.astype(np.float32),
            homography,
        )
        rotated_rectangle = cv2.minAreaRect(projector_contour)
        bounds.append(cv2.boxPoints(rotated_rectangle))

    return bounds


def object_detection():
    logging.basicConfig(level=logging.INFO)
    camera_calibration = calibrate.calibrate()
    logger.info("Calibration complete")

    logger.info("Setting up projector and output window")
    projector = calibrate.get_projector()
    calibrate.make_fullscreen_projector_window(
        "demo",
        projector,
    )
    projector_bounds = get_camera_space_projector_bounds(
        camera_calibration,
        (projector.width, projector.height),
    )

    logger.info("Setting up camera")
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera")

    logger.info("Capturing detection background")
    calibrate.discard_frames(camera, count=10)
    background_frame = calibrate.capture_average(camera, count=10)
    foreground_history: deque[NDArray[np.uint8]] = deque(maxlen=15)

    logger.info("Press q to close the debug windows")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

        # detect objects (contours) in the camera space
        ok, frame = camera.read()
        if not ok:
            raise RuntimeError("Could not read camera frame")

        contours, foreground_mask = detect_objects(
            frame,
            background_frame,
            projector_bounds,
            foreground_history=foreground_history,
        )
        bounds = get_projector_space_object_bounds(
            contours, camera_calibration
        )

        contour_debug = frame.copy()
        cv2.drawContours(contour_debug, contours, -1, (0, 0, 255), 2)
        cv2.polylines(
            contour_debug,
            [np.rint(projector_bounds).astype(np.int32)],
            isClosed=True,
            color=(0, 255, 255),
            thickness=2,
        )
        cv2.imshow(WINDOW_CONTOURS, contour_debug)
        cv2.imshow(WINDOW_FOREGROUND, foreground_mask)

        output = np.zeros(
            (projector.height, projector.width, 3), dtype=np.uint8
        )
        for bound in bounds:
            cv2.polylines(
                output,
                [np.rint(bound).astype(np.int32)],
                isClosed=True,
                color=(0, 255, 0),
                thickness=2,
            )
        cv2.imshow("demo", output)


# def main() -> None:
print("hello")
object_detection()
