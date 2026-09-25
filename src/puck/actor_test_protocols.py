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


canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black") 
coordinates = [(300, 200), (100,200,), (100,100), (300,100)]
## Let's imagine a message, "I am a rectangle and I am at these coordinates. Please draw a rectangle around my coordinates"
fill = "white"
outline = "blue"
width = 3

## In dictionary form, to be added to the drawing queue
dict_message = {"canvas_call": "create_polygon","coordinates":coordinates, "arguments": {"fill": fill, "outline": outline, "width": width}}

## In tuple form, to be added to the drawing queue
tuple_message = (("canvas_call", "create_polygon"), ("arguments", (("coordinates",coordinates),{"fill": fill, "outline": outline, "width": width})))


class Message():
    pass

class DrawingMessage(Message):
    def __init__(self, canvas_call, sender, arguments):
        super().__init__()
        self.canvas_call = canvas_call
        self.arguments = arguments
        self.sender = sender

class InfoMessage(Message):
    def __init__(self, info):
        super().__init__()
        self.info = info


def draw_dict(drawing_queue: Queue, canvas: Canvas) -> None:
    """Draws what is on the drawing queue onto the canvas.

    Args:
        drawing_queue (Queue): the queue that all the actors and main thread can access
        canvas (Canvas): the tkinter graphical space.
    """
    while not drawing_queue.empty():
        print("dequeued")
        m = drawing_queue.get()
        id = getattr(canvas, m["canvas_call"])(m["coordinates"], m["arguments"])
        m["sender"].send({"info":id})
    print("empty queue")

def draw_tuple(drawing_queue: Queue, canvas: Canvas) -> None:
    """Draws what is on the drawing queue onto the canvas.

    Args:
        drawing_queue (Queue): the queue that all the actors and main thread can access
        canvas (Canvas): the tkinter graphical space.
    """
    while not drawing_queue.empty():
        message = drawing_queue.get()
        match message:
            case (("canvas_call", canvas_call), ("sender", sender), ("arguments", arguments)):
                match arguments:
                    case (("coordinates", coordinates), *otherarguments):
                        id = getattr(canvas, canvas_call)(coordinates, otherarguments)
                        sender.send(("id", id))
        canvas.pack()
    print("empty queue")


# obj_message = DrawingMessage(canvas_call = "create_polygon", arguments = {"coordinates": coordinates, "draw_args": {"fill": fill, "outline": outline, "width": width}})

def draw_obj(drawing_queue: Queue, canvas: Canvas) -> None:
    """Draws what is on the drawing queue onto the canvas.

    Args:
        drawing_queue (Queue): the queue that all the actors and main thread can access
        canvas (Canvas): the tkinter graphical space.
    """
    while not drawing_queue.empty():
        message = drawing_queue.get()
        print(type(message))
        match message:
            case DrawingMessage():
                id = getattr(canvas,message.canvas_call)(message.arguments["coordinates"], message.arguments["draw_args"])
                id_message = InfoMessage(info=id)
                message.sender.send(id_message)
        canvas.pack()
    print("empty queue")


def run_dict(self):
    first = self.recieve()
    drawing_queue = first["drawing_queue"]
    drawing_queue.put({"canvas_call": "create_polygon","coordinates":coordinates, "sender":self,"arguments": {"fill": fill, "outline": outline, "width": width}})
    print(self.mailbox)
    while True:
        message = self.recieve()
        print(message)
        if message["info"]:
            print(f"A graphical id I have is: {message["info"]}")


def run_tuple(self):
    first = self.recieve()
    drawing_queue = first["drawing_queue"]
    drawing_queue.put( (("canvas_call", "create_polygon"), ("sender", self), ("arguments", (("coordinates",coordinates),{"fill": fill, "outline": outline, "width": width}))))
    while True:
            message = self.recieve()
            print(message)
            match message:
                case ("id", id):
                    print(f"A graphical id I have is: {id}")


def run_obj(self):
    first = self.recieve()
    drawing_queue = first["drawing_queue"]
    obj_message = DrawingMessage(canvas_call = "create_polygon", sender = self, arguments = {"coordinates": coordinates, "draw_args": {"fill": fill, "outline": outline, "width": width}})
    drawing_queue.put(obj_message)
    while True:
        message = self.recieve()
        match message:
            case InfoMessage():
                print(f"A graphical id I have is: {message.info}")

drawing_queue = Queue()

thisbe = Actor(run_dict)
thisbe.send({"drawing_queue": drawing_queue})
# thisbe.start()
# draw_dict(drawing_queue=drawing_queue, canvas = canvas)


pyramus = Actor(run_tuple)
pyramus.send({"drawing_queue": drawing_queue})
# pyramus.start()
# draw_tuple(drawing_queue=drawing_queue, canvas = canvas)

lion = Actor(run_obj)
lion.send({"drawing_queue": drawing_queue})
lion.start()
draw_obj(drawing_queue=drawing_queue, canvas = canvas)

## Dictionary attempt:
# drawing_queue.put(dict_message)


## Tuple attempt:
# drawing_queue.put(tuple_message)
# draw_tuple(drawing_queue=drawing_queue, canvas = canvas)


## Object attempt:
# drawing_queue.put(obj_message)
# draw_obj(drawing_queue=drawing_queue, canvas = canvas)

canvas.pack()
base.mainloop()
