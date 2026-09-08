from actor import Actor
import time

def draw_loop(self, drawing_actor):
    while True:
        sender, new_message = self.read()
        print(new_message)
        self.send_to(sender,{"type": "canvas_id", "info": 7})
        
        
def draw_triangle(self, drawing_actor):
    self.send_to(drawing_actor, {"action": "new", "info": [(0,0), (2,0), (1,1)]})
    time.sleep(1)
    __, message= self.read()
    triangle_id = message.get("info")
    self.send_to(drawing_actor,{"action": "update", "id": triangle_id,"info": [(0,0), (4,0), (2,2)]})


drawing_actor = Actor(draw_loop, None)
drawing_actor.start()
actor_one = Actor(draw_triangle, drawing_actor)
actor_one.start()
