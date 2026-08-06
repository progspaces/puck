import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.patches as patches

custom = [ "#000000", "#FD1622" ,"#FE00FF", "#00FE16", "#0084FE", "#FEAA0D", "#DB4F89","#EBFB26" ,"#00F8C4" ]
dark = [  "#000000","#2E91E5" , "#E15F99" , "#1CA71C", "#FB0D0D" , "#DA16FF" ,"#B68100" ,"#750D86" ,"#EB663B" ]

def page_setup():
    # Source - https://stackoverflow.com/a
    # Posted by Mahmoud, modified by community. See post 'Timeline' for change history
    # Retrieved 2025-11-20, License - CC BY-SA 4.0
    # This example fits a4 paper with 5mm margin printers

    # figure settings
    figure_width = 28.7 # cm
    figure_height = 20 # cm
    left_right_margin = 1 # cm
    top_bottom_margin = 1 # cm
    # standard a4 paper is 21 cm x 29.7cm

    left   = left_right_margin / figure_width # Percentage from height
    bottom = top_bottom_margin / figure_height # Percentage from height
    width  = 1 - left*2
    height = 1 - bottom*2
    cm2inch = 1/2.54 # inch per cm

    fig = plt.figure(figsize=(figure_width*cm2inch,figure_height*cm2inch))
    ax = fig.add_axes((left, bottom, width, height))
    scaler = 72*cm2inch

    plt.xlim(0, figure_width * width)
    plt.ylim(0, figure_height * height)

    return fig, ax, scaler


def sheet_maker_old(palette = "custom", set_choice = "A"):
    pal = custom if palette == "custom" else dark
    setA = [ "#000000", pal[1], pal[4], pal[6]]
    setB = [ "#000000", pal[1], pal[3], pal[8]]
    setC = [ "#000000", pal[5], pal[7], pal[6]]
    setD = [ "#000000", pal[6], pal[6], pal[6]]
    sets = {"A":setA,"B":setB,"C":setC,"D":setD}
    fig, ax, scaler = page_setup()
    s = np.tile([(2*scaler)**2], 4)
    ax.scatter([1,1,25.5,25.5], [1,17,1,17], c=sets.get(set_choice), s=s)
    plt.axis('off')
    plt.show()
    fig.savefig(f"output/sheets/set_{palette}_{set_choice}.png", dpi=1000)
    fig.savefig(f"output/sheets/set_{palette}_{set_choice}.pdf")



def sheet_maker(int_value, colour_pal, n_col):
    # print(int_value)
    pal = ["#000000"] + colour_pal
    fig, ax, scaler = page_setup()
    s = np.tile([(2*scaler)**2], 4)
    ax.scatter([1,1,25.5,25.5], [1,17,17,1], c=pal, s=s)
    plt.axis('off')
    # plt.show()
    fig.savefig(f"puck/output/sheets/p{n_col}/permutations/p{n_col}_{int_value}.png", dpi=1000)
    fig.savefig(f"puck/output/sheets/p{n_col}/permutations/p{n_col}_{int_value}.pdf")

# This example fits a4 paper with 5mm margin printers
def create_cal_sheet(pal):
    n_col = len(pal) - 1
    edgecolors = ["none"]* len(pal) + ["#000000"] *  (9 - len(pal))
    pal.extend((["#FFFFFF"]*(9 - len(pal))))
    fig, ax, scaler = page_setup()
    s = np.tile([(2*scaler)**2], 9)
    ax.scatter([ 3, 3, 3, 8, 8, 8, 13, 13, 13],[3,8,13,3,8,13,3,8,13], c = pal, linewidths= 4, edgecolors = edgecolors,s = s )
    rect = patches.Rectangle((1, 1), 14.5, 14.5, linewidth=10, edgecolor='black', facecolor='None')
    ax.add_patch(rect)
    # save figure ( printing png file had better resolution, pdf was lighter and better on screen)
    plt.axis('off')
    # plt.show()
    fig.savefig(f"puck/output/sheets/p{n_col}/p{n_col}_calibration.png", dpi=1000)
    fig.savefig(f"puck/output/sheets/p{n_col}/p{n_col}_calibration.pdf")


# create_cal_sheet()
# sheet_maker()