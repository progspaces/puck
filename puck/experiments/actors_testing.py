from actor import Actor
import time
from queue import Queue
from tkinter import *
base = Tk()
base.tk.call('tk', 'scaling', 2.0)
## Name of the window you're opening
base.title('Tkinter Widget Size')
## 1920x1080, display size, +0+-1080 repositioning
base.geometry("1920x1080+0+-1080")
## set to be fullscrean
# base.wm_attributes("-fullscreen", True)


def draw_loop(drawing_queue, canvas):
    while True:
        (sender, new_message)= drawing_queue.get()
        print(sender)
        if new_message.get("type") == "kill":
            break
        elif new_message.get("action") == "new":
            id = canvas.create_polygon(new_message.get("info"), outline='blue',fill="white", width=2)
            sender.read_only_message({"type": "canvas_id", "canvas_id": id})
        elif new_message.get("action") == "new":
            id = new_message.get("id")
            canvas.coords(id, new_message.get("info"))
    print("end of draw_loop")

        
        
def draw_triangle(self):
    _, message = self.read()
    print(message)
    assert message.get("type") == "drawing_queue"
    drawing_queue = message.get("drawing_queue")
    drawing_queue.put((self, {"action": "new", "info": [(0,0), (2,0), (1,1)]}))
    time.sleep(1)
    __, message= self.read()
    print(message)
    assert message.get("type") == "graphics_id"
    triangle_id = message.get("graphics_id")
    drawing_queue.put((self, {"action": "update", "id": triangle_id,"info": [(0,0), (4,0), (2,2)]}))
    time.sleep(2)
    drawing_queue.put((None, {"type": "kill"}))


cheight, cwidth = 1080,1920
canvas = Canvas(height= cheight, width = cwidth, background='black')
canvas.pack()
drawing_queue = Queue()
actor_one = Actor(draw_triangle)
actor_one.start()
actor_one.read_only_message({"type": "drawing_queue", "drawing_queue": drawing_queue})
actor_one.read_only_message({"type": "graphics_id", "graphics_id": 1})
print("pre draw loop")
draw_loop(drawing_queue, canvas)
print("post draw loop")
canvas.pack()
base.mainloop()




def single_call_at_start(base):
    cheight, cwidth = 1080,1920
    canvas = Canvas(height= cheight, width = cwidth, background='black')
    canvas.pack()

    drawing_queue = Queue()

    def update():
        actor_one = Actor(draw_triangle)
        actor_one.start()
        actor_one.read_only_message({"type": "drawing_queue", "drawing_queue": drawing_queue})
        actor_one.read_only_message({"type": "graphics_id", "graphics_id": 1})

    base.after(20, update,code)
    print("pre mainloop")
    base.mainloop()
    print("post mainloop")