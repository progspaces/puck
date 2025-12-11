import cv2
import click

@click.command()
def webcamCapture():
    vc = cv2.VideoCapture(0) # input index is 0, so first video input I assume 
        # returns a viedos capture object called vc
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read() # 
        while rval:
            cv2.imshow("preview", frame)
            rval, frame = vc.read() 
            key = cv2.waitKey(20)
            if key == 32: # exit on ESC
                cv2.imwrite(f"snapshot.jpg", frame)
            elif key == 27: # exit on ESC
                break

    cv2.destroyWindow("preview")
    vc.release()    

    ### @click.command() and the next line is what is passed into the command function, and whatever is returned is the new value of webcamCapture
    ### wraps it up as a click.command object and then assigns it to the name webcamCaputre
    ### ways of enriching the function with more funcitonality in a way that is orthogonal to the function definition.


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="s,"
)
def estimate_idim(config: Path):
    """
    Entry point for the CLI.

    Parameters
    ----------
    config : Path
        Path to storage folder
    """
    click.echo(f"Using config file: {config}")

    # load in the config
    cfg = ExperimentConfig.from_json(config) ##. CONFIG FOR EXPERIMENT
    ctx = ExperimentContext(DATA_HOME=os.getenv("DATA_ROOT")) ### PATH
    
    print('Starting experiment run ...')
    print(cfg)
    print(ctx)

