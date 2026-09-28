# Setup tkinter early (
# necessary on MacOS).
from tkinter import *  
base = Tk()

from queue import Queue
base.tk.call("tk", "scaling", 2.0)
base.title("Tkinter Widget Size")
base.wm_attributes("-fullscreen", True)
CANVAS_HEIGHT, CANVAS_WIDTH = 1080, 1920
from actor import Actor
from contents import FunctionContents, Contents
from messages import Dialogue, Monologue


canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black") 
coordinates = [(300, 200), (100,200,), (100,100), (300,100)]
## Let's imagine a message, "I am a rectangle and I am at these coordinates. Please draw a rectangle around my coordinates"
fill = "white"
outline = "blue"
width = 3

def test_run():
    pass

def test_read(drawing_queue: Queue, canvas: Canvas) -> None:
   while not drawing_queue.empty():
            message = drawing_queue.get()
            match message:
                case Dialogue(contents,sender):
                    match contents:
                        case FunctionContents(call,args,kwargs):
                            id = call(canvas,args, kwargs)
                            sender.send( Monologue(contents = Contents(content = id)))
                        case _ as other_content:
                            print(f"You have given me an unknown contents, I do not know how to handle {other_content}")
                case Monologue(contents = contents):
                    print("this is a monologue, we do not respond to")
                case _ as unknown:
                    print(f"You have given me an unknown message, I do not know how to handle {unknown}")



test_contents = FunctionContents(function_call = Canvas.create_polygon, 
                                args =coordinates, 
                                kwargs = {"fill": fill, "outline": outline, "width": width})
test_actor = Actor(target = test_run)

test_message = Dialogue(contents = test_contents, sender = test_actor)

drawing_queue = Queue()
drawing_queue.put(test_message)

test_read(drawing_queue=drawing_queue, canvas=canvas)

canvas.pack()
base.mainloop()
