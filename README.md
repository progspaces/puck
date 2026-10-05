# Puck
*"that shrewd and knavish sprite"*

## What is it?
Puck is an implementation of a programmable space that takes in visual input from a generic webcam and uses that to generate different projections. It does this by recognizing physical pieces of paper which are placed on a table in front of the camera. These papers are associated with user defined code which generate a response in the system, typically using projections. When the programs are moved about, the system registers their physical movement and reacts accordingly, allowing dynamic spatial input and output using light and paper.

### Inspiration / Other Similar pojects
Programmable Spaces: DynamicLand, LivingRoom, Spatial Pixel, Folk Computer.

Historical: SmallTalk, Liveboard, Wellner's DigitalDesk, MIT Media Lab's MetaDesk. 


## Who made it?
This project is maintained at the School of Computer Science of the University of St Andrews by the Programmable Spaces group.

## How do I use it?

Dependancies

You will need
- Python: This project depends on Python 3.14 or higher
- UV: Please install UV as it is our package manager for this project.

TODO: add more detail here.

## Puck Files in this Repo

## Main

## Geometry Module
This module handles all of the geometric commands Puck uses. It will be called in main but will not be necessary to explore in individual applications unless to debug interactions with main.py

To read more about this please read the docstring at the beginning of the module.

## Actor System
Inspired by Erlang's actor system, we have implemented an Actor class which extends the Python thread class. It has a generalized Actor class as well as a more specific DrawingActor subsclass which directly interacts with graphics generation. Both, as extensions of threads, need a target function which they will run upon calling `[actor].start()`. This allows each program to run in its own thread and communicate with each other and the main thread with message passing.

To read more about this please read the docstring at the beginning of the Actor module.


## Contact information

Please reach out to us at the following emails to collaborate or if you have any outstanding questions after reading the documentation provided:

Julia Dreiling jmcd1@st-andrews.ac.uk


David Morrison dm236@st-andrews.ac.uk


Michael Young mct25@st-andrews.ac.uk

If you see any issues please open an issue on this repo and we will get to it as soon as we can. You can also open a pull request as you see fit and we will evaluate it as a group.

## Our Other Projects

Previous work in this space include Julia's Moth domain specific programing language for programmable spaces as well as Naveen Vatti's MothVision computer vision system for programmable spaces.

