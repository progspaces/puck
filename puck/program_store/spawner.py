## grab what items the program is going to create
from tkinter import *

def creation(id, item,canvas, base):
    type =  item.get("type")
    if type == "text":            
        text_item = canvas.create_text((600,50),text=item.get("display_text"),font=("Helvetica", 50), fill= "White")
        return {id: text_item}
    elif type == "shape":
        shape_type = item.get("shape_type")
        if shape_type == "square":
            square_item = canvas.create_polygon((0,0), (0,0), (0,0), (0,0),
                                outline='blue',fill="white", width=2)
            return {id:square_item}
        elif shape_type == "circle":
            points = item.get("points")
            circle_item = canvas.create_oval(points)
            return {id:circle_item}
        elif shape_type == "polygon":
            points = item.get("points")
            polygon_item = canvas.create_polygon(points,
                                outline='blue',fill="white", width=2)
            return {id:polygon_item}
        else:
            return Exception("shape type not recognized")
    elif type == "image":
        image = Image(base,)
        return {id:image}
    else:
        return Exception("item type not recognized")
    

for id, item in item_dict.items():
    id_item_pair = creation(id, item ,canvas, base)
    graphics_storage.update(id_item_pair)

