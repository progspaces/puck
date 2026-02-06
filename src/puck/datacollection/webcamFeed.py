import cv2
import click
from itertools import product
import os
from threading import Thread



PALETTES = ["custom", "dark"]
PERMS = ["A", "B", "C", "D"]
DISTS = ["high", "medium", "short"]
ROOMS = ["john_honey","davids", "michaels", "jack_cole",]
COUNTS = range(5)

variants = product(PALETTES,ROOMS,DISTS,PERMS,COUNTS)

# def showPreview():
#     vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
#     while True:
#         rval, frame = vc.read()
#         while not rval:
#             print("Something is wrong with the camera, rval is false, press a key when fixed")
#             key = cv2.waitKey(0)
#         print(f"this is rval{rval}")
#         cv2.imshow("preview", frame)
#         key = cv2.waitKey(20)
#         if key == 27: # exit on ESC
#             break




@click.command()
def webcamCapture():
    i = 0
    vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
        # returns a viedos capture object called vc
    # thread1 = Thread(target = showPreview)
    if vc.isOpened(): # try to get the first frame
        # thread1.start()
        # for palette,room,dist,perm,count in variants:
        palette = "dark"
        room = "davids"
        dist = "high"
        perm = "B"
        count = 0
        print(i)
        i += 1
        directory = f"{palette}/{room}/{dist}/{perm}/"
        file_name = f"{palette}_{room}_{dist}_{perm}_{count}.jpg"
        os.makedirs(directory,exist_ok=True)
        path_name = directory + file_name
        rval, frame = vc.read() 
        cv2.imshow("preview", frame)
        while True:
            print(f"Press space to take {path_name}")
            key = cv2.waitKey(0)
            print("HIHIHIHIHIHI")
            print(key)
            rval, frame = vc.read() 
            if not rval:
                print("Something is wrong with the camera, rval is false, press a key when fixed")
            elif key == 112:
                cv2.imshow("preview", frame)
            elif key == 32: #space to capture
                cv2.imwrite(f"{path_name}", frame)
                break
    cv2.destroyWindow("preview")
    vc.release()    

    ### @click.command() and the next line is what is passed into the command function, and whatever is returned is the new value of webcamCapture
    ### wraps it up as a click.command object and then assigns it to the name webcamCaputre
    ### ways of enriching the function with more funcitonality in a way that is orthogonal to the function definition.


# @click.command()
# @click.option(
#     "--config",
#     "-c",
#     type=click.Path(exists=True, dir_okay=False),
#     required=True,
#     help="s,"
# )
# def estimate_idim(config: Path):
#     """
#     Entry point for the CLI.

#     Parameters
#     ----------
#     config : Path
#         Path to storage folder
#     """
#     click.echo(f"Using config file: {config}")

#     # load in the config
#     cfg = ExperimentConfig.from_json(config) ##. CONFIG FOR EXPERIMENT
#     ctx = ExperimentContext(DATA_HOME=os.getenv("DATA_ROOT")) ### PATH
    
#     print('Starting experiment run ...')
#     print(cfg)
#     print(ctx)