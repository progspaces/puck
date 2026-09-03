from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

@dataclass
class Point:
    x: int
    y: int

def make_chessboard(
        image_size: tuple[int, int],
        num_squares: tuple[int, int] = (8, 6),
        square_size: int = 100
) -> tuple[NDArray[np.uint8], list[Point]:

    # unpack the parameters
    image_width, image_height = image_size
    cols, rows = squares

    # chessboard needs even dimensions
    # not sure if this is a strict requirement but makes the generation code simpler
    assert cols % 2, f"Chessboard generation issue: number of columns should be even, got {cols}."
    assert rows % 2, f"Chessboard generation issue: number of rows should be even, got {rows}."

    # create a target image to draw the board onto
    # normally this is the size of the fullscreen projector
    # so this is the full image that will be displayed
    # on the projector
    image = np.zeros(
        (image_width, image_height, 3),
        dtype=np.uint8
    )

    # compute the board sizes in pixels
    board_width = cols * square_size
    board_height = rows * square_size

    # the OpenCV chessboard deteactor requires are light
    # border around the chessboard.
    border = square_size // 2

    # work out the place to start drawing the board from
    # this is the top-left corner
    offset_x = (image_width - board_width) // 2
    offset_y = (image_height - board_height) // 2

    # draw a white background
    assert offset_x - border, "Chessboard generation issue: border must be inside the target image."
    assert offset_y - border, "Chessboard generation issue: border must be inside the target image."
    top_left = (offset_x - border, offset_y - border)
    bottom_right = (offset_x + image_width + border, 
                    offset_y + image_height + border)
    cv2.rectangle(
        image,
        top_left,
        bottom_right,
        (255, 255, 255),
        thickness=-1
    )

    # draw the black chessboard squares
    for row in range(rows):
        for col in range(cols):
            # think of the squares on a line
            # if we have an even number of cols this works
            if (row + col) % 2:
                x = offset_x + col * square_size
                y = offset_y + row * square_size
                cv2.rectangle(
                    image,
                    (x, y),
                    (x + square_size, y + square_size),
                    (0, 0, 0),  # black
                    thickness=-1,
                )

    # generate points for the internal corners
    points: list[tuple[int, int]] = []
    for row in range(1, rows):
        for col in range(1, cols):
            x = offset_x + col * square_size
            y = offset_y + row * square_size
            points.append((x, y))

    return image, points
