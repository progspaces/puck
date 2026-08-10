from tkinter import *
def on_start(owned_graphics: list[int], canvas:Canvas, box:int):
    hello = canvas.create_text((500,500),text="hello world",font=("Helvetica", 50), fill= "blue")
    owned_graphics.append(hello)

def on_update(owned_graphics: list[int], canvas:Canvas, box:int):
    print("hello update")
    pass

def on_the_destruction_and_the_salting_of_the_earth():
    pass #you shall not