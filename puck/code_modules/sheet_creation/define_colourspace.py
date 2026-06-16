## How many unique colours do i need to create a permutation of 3
## The obvious thing is a b c, which gets me back 27 permutations, that should be sufficient
## So min 3, we've done up to 8 which is 8^3 

# I want it to generate these + white and black as the colours 
# R Code below: 
'''
# library(Polychrome)
# set.seed(82000)
# p8_n = 2+8
# seedcolors = c("#000000", "#FFFFFF")
# range = c(0,1000)
# ylim=c(0, 180)

# p8_n = 2+8
# p7_n = 2+7
# p6_n = 2+6
# p5_n = 2+5
# p4_n = 2+4
# p3_n = 2+3

# p8 = createPalette(p8_n, seedcolors, range=range)
# print(p8)
# p8Dists = plotDistances(p8, ylim=ylim)
# swatch(p8)


# p7 = createPalette(p7_n, seedcolors, range=range)
# print(p7)
# p7Dists = plotDistances(p7, ylim=ylim)
# swatch(p7)

# p6 = createPalette(p6_n, seedcolors, range=range)
# print(p6)
# p6Dists = plotDistances(p6, ylim=ylim)
# swatch(p6)

# p5 = createPalette(p5_n, seedcolors, range=range)
# print(p5)
# p8Dists = plotDistances(p5, ylim=ylim)
# swatch(p5)

# p4 = createPalette(p4_n, seedcolors, range=range)
# print(p4)
# p4Dists = plotDistances(p4, ylim=ylim)
# swatch(p4)

# p3 = createPalette(p3_n, seedcolors, range=range)
# print(p3)
# p3Dists = plotDistances(p3, ylim=ylim)
# swatch(p3)
# 
'''

import puck.code_modules.sheet_creation.sheets as sheets
import pprint
import json 

def to_base(number, base):
    """Converts a non-negative number to a list of digits in the given base.

    The base must be an integer greater than or equal to 2 and the first digit
    in the list of digits is the most significant one.
    """
    digits = []
    while number:
        digits.append(number % base)
        number //= base
    base_array = list(reversed(digits))
    while len(base_array) < 3: ## the 3 represents the 3 spaces for the digits, ie the 3 dots possible
        base_array.insert(0,0) ## 0 must be added because this doesn't add the leading 0s
    return base_array


def translate_perm_to_int(perm, palette , base):
    base_array = [palette.index(x) for x in perm]
    return int(''.join(str(x) for x in base_array), base)


polychrome_dictionary = {3:["#FE0D16", "#00F916","#1683FC"]}

n_colours = 3
colour_palette = polychrome_dictionary.get(n_colours)
colour_palette_w_black = ["#000000"] + colour_palette

# sheets.create_cal_sheet(pal = colour_palette_w_black) 

def colour_perm(number, n_colours, colour_palette):
    index_list = to_base(number,n_colours)
    # print(index_list)
    return [colour_palette[x] for x in index_list]


# int_to_colour_perm = {x:colour_perm(x,n_colours,colour_palette) for x in range(0,n_colours**3)}


## This is a list comprehension generated dictionary
## We generate a list of all the integers that can be represented, range(0,n_colours**3)
## in the case of n_colours = 4, that would be 4^3, n_colours**3
## then we generate the corresponding colour permutations using the palette (sans black), colour_perm(x,n_colours,colour_palette)
## and make a dicitonary that assigns those to their corresponding integer, x:colour_perm(x,n_colours,colour_palette)
def main():

    int_to_colour_perm = {x:colour_perm(x,n_colours,colour_palette) for x in range(0,n_colours**3)[0:10]}

    ## Make permutation sheets
    for k,v in int_to_colour_perm.items(): sheets.sheet_maker(k,v, n_colours)

    with open(f'puck/output/polychrome_lookup.json', 'w') as fp:
        json.dump(polychrome_dictionary, fp, indent=3)

# main()
