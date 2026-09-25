# Setup tkinter early (
# necessary on MacOS).
from tkinter import *  
base = Tk()

from queue import Queue
base.tk.call("tk", "scaling", 2.0)
base.title("Tkinter Widget Size")
base.wm_attributes("-fullscreen", True)
CANVAS_HEIGHT, CANVAS_WIDTH = 1080, 1920

canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black") 
coordinates = [(300, 200), (100,200,), (100,100), (300,100)]
## Let's imagine a message, "I am a rectangle and I am at these coordinates. Please draw a rectangle around my coordinates"
fill = "white"
outline = "blue"
width = 3
from messages import DrawingContents, Monologue


## FUNCTOOLS - > Partial 
## COmpose function into partial


test_contents = DrawingContents(canvas_call = Canvas.create_polygon, 
                                args =coordinates, 
                                kwargs = {"fill": fill, "outline": outline, "width": width})

test_message= Monologue(contents = test_contents)


def test_read(drawing_queue: Queue, canvas: Canvas) -> None:
    message = drawing_queue.get()
    match message:
        case Monologue(contents = DrawingContents(canvas_call = call, args = args, kwargs = kwargs)):
            print("reached monologue")
            id = call(canvas, args, kwargs)
            print(id)
        # case 

drawing_queue = Queue()
drawing_queue.put(test_message)
test_read(drawing_queue=drawing_queue, canvas=canvas)

canvas.pack()
base.mainloop()