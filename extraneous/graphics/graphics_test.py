from tkinter import *
import tkinter.font as tkFont

def circle(canvas,center_coord, radius,fill_color=None, outline_color= "black", outline_thickness = 1):
    x = center_coord[0]
    y = center_coord[1]
    half_rad = radius/2
    canvas.create_oval(x-half_rad,y-half_rad, x+half_rad, y+half_rad,fill=fill_color, outline=outline_color, width = outline_thickness)

def square(canvas:Canvas, corner_coord,side, fill_color=None, outline_color= "black", outline_thickness= 1):
    corner_x = corner_coord[0]
    corner_y = corner_coord[1]
    canvas.create_rectangle(corner_x,corner_y, corner_x+side, corner_y+side, fill=fill_color, outline=outline_color, width = outline_thickness)

def image_formatted(src, scale_xy= (1,1),scale_direction = None):
    image_obj = PhotoImage()
    image_obj.read(src)
    if scale_direction == "bigger":
        image_obj = image_obj.zoom(scale_xy[0], scale_xy[1])  
    elif scale_direction == "smaller":
        image_obj = image_obj.subsample(scale_xy[0], scale_xy[1])  
    return image_obj

def text(canvas, location_coords, text, size=10):
    font_choice = tkFont.Font(size=size)
    canvas.create_text(location_coords, text=text,font=font_choice)

def root_setup(root_width = '1200',root_height = '800',root_x = '0',root_y = '0'):
    root = Tk()
    root.geometry(f'{root_width}x{root_height}+{root_x}+{root_y}')
    return root, root_width, root_height

def canvas_setup(root, root_width, root_height):
    root = Tk()
    canvas_width = int(root_width)
    canvas_height = int(root_height)
    C = Canvas(root,width = canvas_width, height = canvas_height)
    # C= None
    return C, canvas_width,canvas_height

def display(root, C):
    C.pack()
    root.mainloop()


def main():
    ## SETUPS
    root, root_width, root_height = root_setup()
    C, canvas_width,canvas_height=  canvas_setup(root, root_width, root_height)
    ## GET CENTER
    canvas_center = (canvas_width/2, canvas_height/2)
    ## text
    text_sample = "sample text"
    text(C,canvas_center,text=text_sample, size =122)
    # C.create_text(canvas_center, text=text_sample)
    ## shape
    circle(C,canvas_center,radius=100)
    ## image
    src="puck/graphics/cat.jpg"
    image_obj = image_formatted(src=src,scale_direction="smaller",scale_xy=(2,2))
    C.create_image(canvas_center[0]-500, canvas_center[1]-200, image= image_obj)
    ## Display
    display(root, C)

# main()