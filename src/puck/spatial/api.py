from chorus import me, Proxy
from ..geometry import Polygon
from PIL import Image
import tkinter as tk

def corners(spatial: Proxy) -> list[Polygon]:
    corners: list[Polygon] = spatial.ask.corners(me())
    return corners


def create_polygon(canvas: Proxy, polygon: Polygon) -> int:
    points = polygon.flat_unwrap()
    shape_id: int = canvas.ask.create_polygon(points, fill="white")
    return shape_id


def update_polygon(canvas: Proxy, graphical_id: int, polygon: Polygon) -> None:
    points = polygon.flat_unwrap()
    canvas.tell.coords(graphical_id, points)


def images(spatial: Proxy) -> list[Polygon]:
    images: list[Polygon] = spatial.ask.images(me())
    return images

def create_image(canvas: Proxy, img: Image) -> int:
    image_id: int = canvas.ask.create_image(100, 100, image=img, anchor = tk.NW)
    return image_id