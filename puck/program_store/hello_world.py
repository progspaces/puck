from tkinter import *
from tkinter import font
def on_start(owned_graphics: list[int], canvas:Canvas, box:int):
    ## get the box coordinates
    box_x0, box_y0,box_x1, box_y1,  box_x2, box_y2, box_x3, box_y3= (canvas.coords(box))
    hello = canvas.create_text(( box_x0, box_y0),text="hello world",font=("Helvetica", 50), fill= "blue")
    owned_graphics.append(hello)

def on_update(owned_graphics: list[int], canvas:Canvas, box:int):
    print("hello update")
    box_x0, box_y0,box_x1, box_y1,  box_x2, box_y2, box_x3, box_y3= (canvas.coords(box))
    
    print(f"box coords: {box_x0, box_y0,}")
    text_is = (canvas.itemcget(owned_graphics[0], "text"))
    font_test = font.Font(font=canvas.itemcget(owned_graphics[0], 'font'))    
    print()
    distance = font_test.measure(text_is)
    print(distance)
    mean_box_x = sum([box_x0,box_x1,box_x2,box_x3])/4
    mean_box_y = sum([box_y0,box_y1,box_y2,box_y3])/4
    canvas.moveto(owned_graphics[0],mean_box_x - distance/2, mean_box_y-font_test.cget("size"),)
    pass

def on_the_destruction_and_the_salting_of_the_earth():
    pass #you shall not