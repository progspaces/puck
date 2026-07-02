from tkinter import *
from tkinter import ttk
import time

root = Tk()
v = StringVar() 
v.set("Helloooooo")
lbl = Label(root, textvariable= v)
lbl.pack()

def task():
    previous = v.get()
    if len(previous)==200: # Stopping condition
        root.quit()
    v.set(previous+ "o") ## Update condition
    root.after(20, task)  # Timed Check, adding itself back onto the queue to run 20ms later

root.after(20, task) ## First after call (starts the recursive loop)
root.mainloop()