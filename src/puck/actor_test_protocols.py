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
from messages import Dialogue, Monologue, Contents, DrawingContents


canvas = Canvas(base, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, background="black") 
coordinates = [(300, 200), (100,200,), (100,100), (300,100)]
## Let's imagine a message, "I am a rectangle and I am at these coordinates. Please draw a rectangle around my coordinates"
fill = "white"
outline = "blue"
width = 3

def test_run():
    pass

test_contents = DrawingContents(canvas_call = "create_polygon", 
                                args =coordinates, 
                                kwargs = {"fill": fill, "outline": outline, "width": width})

test_actor = Actor(target = test_run)
test_message = Dialogue(contents = test_contents, sender = test_actor)


def test_read(drawing_queue: Queue, canvas: Canvas) -> None:
   while not drawing_queue.empty():
            message = drawing_queue.get()
            match message:
                case Dialogue(contents=DrawingContents(canvas_call = call, args = args, kwargs = kwargs), sender = sender):
                    id = getattr(canvas,call)(args,kwargs)
                    sender.send( Monologue(contents = Contents(content = id)))
                case Monologue(contents = contents):
                    print("this is a monologue, we do not respond to")
                case _ as unknown:
                    print(f"You have given me an unknown message, I do not know how to handle {unknown}")


canvas.create_polygon()(args, kwargs)

drawing_queue = Queue()
drawing_queue.put(test_message)
test_read(drawing_queue=drawing_queue, canvas=canvas)

# def draw_obj(drawing_queue: Queue, canvas: Canvas) -> None:
#     """Draws what is on the drawing queue onto the canvas.

#     Args:
#         drawing_queue (Queue): the queue that all the actors and main thread can access
#         canvas (Canvas): the tkinter graphical space.
#     """
#     while not drawing_queue.empty():
#         message = drawing_queue.get()
#         print(type(message))
#         match message:
#             case Dialogue():
#                 id = getattr(canvas, message.canvas_call)(message.arguments["coordinates"], message.arguments["draw_args"])
#                 id_message = m.InfoMessage(info=id)
#                 message.sender.send(id_message)
#         canvas.pack()
#     print("empty queue")




# def run_obj(self):
#     first = self.recieve()
#     drawing_queue = first["drawing_queue"]
#     obj_message = m.DrawingMessage(canvas_call = "create_polygon", 
#                                  sender = self, 
#                                  arguments = {"coordinates": coordinates, "draw_args": {"fill": fill, "outline": outline, "width": width}})
#     drawing_queue.put(obj_message)
#     while True:
#         message = self.recieve()
#         match message:
#             case m.InfoMessage():
#                 print(f"A graphical id I have is: {message.info}")

# # drawing_queue = Queue()


# lion = Actor(run_obj)
# lion.send({"drawing_queue": drawing_queue})
# lion.start()
# draw_obj(drawing_queue=drawing_queue, canvas = canvas)

# canvas.pack()
# base.mainloop()
