from tkinter import *
from tkinter import font
import math
from statistics import mean

def rad2deg(value):
    return value * (180/math.pi)


def on_start(owned_graphics: list[int], canvas:Canvas, box:int):
    ## get the box coordinates
    x0, y0,_,_,_,_,_,_= (canvas.coords(box))
    hello = canvas.create_text(( x0, y0),text="hello world",font=("Helvetica", 50), fill= "blue")
    owned_graphics.append(hello)


def center(canvas, box):
    box_coordinates = canvas.coords(box)
    box_x = [box_coordinates[i] for i in range(len(box_coordinates)) if i%2 == 0]
    box_y = [box_coordinates[i] for i in range(len(box_coordinates)) if i%2 == 1]
    return mean(box_x),mean(box_y)

def rotate(canvas, box, side_xs, side_ys):
    mean_box_x, mean_box_y =center(canvas, box)
    midline_point = (mean(side_xs),mean(side_ys))
    angle_deg = rad2deg(math.atan2((mean_box_y-midline_point[1]),(mean_box_x-midline_point[0])))
    return angle_deg

def follow_paper(canvas, box, id, point_or_side = "point", location = "center", rotation = True):
    x0,y0, x1,y1, x2,y2,x3,y3= canvas.coords(box)
    if rotation:
        angle_deg = rotate(canvas, box, side_xs=[x0,x1], side_ys=[y0,y1])
        canvas.itemconfig(id,angle=-angle_deg)

    if point_or_side == "point":
        if location == "centre" or location == "center":
            point_x,point_y = center(canvas=canvas, box=box)
        elif location =="bottom_left":
            point_x,point_y = (x0,y0)
        elif location == "top_left":
             point_x,point_y = (x1,y1)
        elif location == "top_right":
            point_x,point_y = (x2,y2)
        elif location == "bottom_right":
            point_x,point_y = (x3,y3)
        else:
            point_x,point_y = (0,0) ## default point
    else: ## implication here being side
        if location == "left":
            point_x,point_y =(mean([x0,x1]),mean([y0,y1]))  ## default side
        elif location =="right":
            point_x,point_y = (mean([x2,x3]),mean([y2,y3])) 
        elif location == "top":
            point_x,point_y =  (mean([x1,x2]),mean([y1,y2])) 
        elif location == "bottom":
            point_x,point_y =(mean([x0,x3]),mean([y0,y3])) 
        else:
            point_x,point_y = (0,0) ## default point
            
    if str(canvas.type(id)) == "text":
        value = canvas.itemcget(id, "text")
        font_test = font.Font(font=canvas.itemcget(id, 'font'))    
        distance = font_test.measure(value)
        point_x = point_x - distance/2,  

    canvas.moveto(id,point_x, point_y)
    

def on_update(owned_graphics: list[int], canvas:Canvas, box:int):
    for i in owned_graphics:
        follow_paper(canvas, box, i, point_or_side="point", location="center", rotation = True)

def on_the_destruction_and_the_salting_of_the_earth(owned_graphics: list[int], canvas:Canvas, box:int):
    for i in owned_graphics:
        canvas.delete(i)
    owned_graphics = []

