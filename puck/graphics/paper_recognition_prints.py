import puck.graphics.graphics_test as graphics_functions
# from tkinter import Tk; 
# from tkinter import *
# from tkinter import ttk
# import tkinter.font as tkFont


def recognize(base, permutation, stop_tk, paper_coordinates = [(100,100),(400,200)]):
    while not stop_tk:
        print(permutation)
        integer_val = int(permutation,3)
        C, canvas_width, canvas_height = graphics_functions.canvas_setup(base, 1200, 800)
        canvas_center = (canvas_width/2, canvas_height/2)
        display_text= f"{permutation}\nThis is number: {str(integer_val)}"
        C.create_rectangle(paper_coordinates)
        graphics_functions.text(canvas=C, location_coords=canvas_center, text=display_text,size=100)
        
    base.destroy()

# recognize("001")