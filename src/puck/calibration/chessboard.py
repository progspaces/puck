from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray


@dataclass
class Point:
    x: int
    y: int


def make_chessboard(
    image_size: tuple[int, int] = (1920, 1080),
    squares: tuple[int, int] = (8, 6),
    square_size: int = 100,
) -> tuple[NDArray[np.uint8], list[tuple[int, int]]]:
    """Create a centred chessboard calibration pattern.

    Args:
        image_size:
            Image dimensions as (width, height).
        squares:
            Number of chessboard squares as (columns, rows).
        square_size:
            Width and height of each square in pixels.

    Returns:
        A tuple containing:
        - The generated BGR image.
        - The projector coordinates of the internal chessboard corners.
    """
    image_width, image_height = image_size
    cols, rows = squares

    # assert col % 2 == 0, "Chessboard "

    board_width = cols * square_size
    board_height = rows * square_size

    offset_x = (image_width - board_width) // 2
    offset_y = (image_height - board_height) // 2

    image: NDArray[np.uint8] = np.zeros(
        (image_height, image_width, 3),
        dtype=np.uint8,
    )

    # Chessboard detectors need a light border around the pattern. Without it,
    # black edge squares merge into the black projection background and the
    # contour-based detector cannot identify the board reliably.
    border = square_size // 2
    cv2.rectangle(
        image,
        (max(0, offset_x - border), max(0, offset_y - border)),
        (
            min(image_width - 1, offset_x + board_width + border),
            min(image_height - 1, offset_y + board_height + border),
        ),
        (255, 255, 255),
        thickness=-1,
    )

    # Draw the black chessboard squares on the light backing.
    for row in range(rows):
        for col in range(cols):
            if (row + col) % 2 == 0:
                x = offset_x + col * square_size
                y = offset_y + row * square_size

                cv2.rectangle(
                    image,
                    (x, y),
                    (x + square_size, y + square_size),
                    (0, 0, 0),
                    thickness=-1,
                )

    # Internal corners only.
    points: list[tuple[int, int]] = []

    for row in range(1, rows):
        for col in range(1, cols):
            x = offset_x + col * square_size
            y = offset_y + row * square_size
            points.append((x, y))

    return image, points
