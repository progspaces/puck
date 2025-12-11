import click

from dotenv import load_dotenv
load_dotenv()

from puck.cli.webcamFeed import webcamCapture

@click.group(help = "CLI tool to take and process images for experimentating to get hyperparameters")
def cli():
    pass

cli.add_command(webcamCapture)

def main():
    cli(prog_name="puck")

if __name__ == "__main__":
    main()