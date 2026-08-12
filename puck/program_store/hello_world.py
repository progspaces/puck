from tkinter import *
from tkinter import font
import math
import numpy as np

def vectors(p0, p1, p2):
    v10 = (p1[0] - p0[0] ,p1[1] - p0[1] )
    v12 =  (p1[0] - p2[0],p1[1] - p2[1])
    return (v10,v12)

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.dot(v1_u, v2_u))

print(f"{np.rad2deg(angle_between((0,1),(1,0)))}")

def on_start(owned_graphics: list[int], canvas:Canvas, box:int):
    ## get the box coordinates
    box_x0, box_y0,box_x1, box_y1,  box_x2, box_y2, box_x3, box_y3= (canvas.coords(box))
    ## Store the angle of 0, to 1, to 2, 
    print(f"The coords are 0: { box_x0, box_y0}, 1:{box_x1, box_y1 },2:{ box_x2,box_y2,}")
    hello = canvas.create_text(( box_x0, box_y0),text="hello world",font=("Helvetica", 50), fill= "blue")

    owned_graphics.append(hello)

def on_update(owned_graphics: list[int], canvas:Canvas, box:int):
    box_coordinates = canvas.coords(box)
    box_x = [box_coordinates[i] for i in range(len(box_coordinates)) if i%2 == 0]
    box_y = [box_coordinates[i] for i in range(len(box_coordinates)) if i%2 == 1]
    box_x0, box_y0,box_x1, box_y1,  box_x2, box_y2, box_x3, box_y3= (canvas.coords(box))
    ## Store the angle of 0, to 1, to 2, 
    print(f"The coords are 0: { box_x0, box_y0}, 1:{box_x1, box_y1 },2:{ box_x2,box_y2,}")
    vecs= vectors((box_x0, box_y0),( box_x1,box_y1,),(0, 0))
    angl = angle_between(vecs[0], vecs[1])
    # angle_deg = np.rad2deg(angle_between(vecs[0], vecs[1]))
   
    # print(angle_deg, angl)
    text_is = (canvas.itemcget(owned_graphics[0], "text"))
    font_test = font.Font(font=canvas.itemcget(owned_graphics[0], 'font'))    
    distance = font_test.measure(text_is)
    # print(distance)
    mean_box_x = sum(box_x)/len(box_x)
    mean_box_y = sum(box_y)/len(box_y)
    angle_deg= np.rad2deg(math.atan2((mean_box_y-box_y0),(mean_box_x-box_x0)))
    canvas.moveto(owned_graphics[0],mean_box_x - distance/2, mean_box_y-font_test.cget("size"),)
    print(f"angle previously:{ (canvas.itemcget(owned_graphics[0], "angle"))}")
    canvas.itemconfig(owned_graphics[0], angle=-angle_deg)
    print(f"angle now:{ (canvas.itemcget(owned_graphics[0], "angle"))}")


def on_the_destruction_and_the_salting_of_the_earth(owned_graphics: list[int], canvas:Canvas, box:int):
    for i in owned_graphics:
        canvas.delete(i)
    owned_graphics = []