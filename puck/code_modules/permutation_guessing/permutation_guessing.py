import colorsys
import puck.code_modules.colour_conversion.colour_conversion as conv
from math import sqrt






def get_color_perm(ordered_rectangle, n_colours, true_colors,printing:bool = False, colorspace:str = "LUV"):
    ordered_colors = [c[1] for c in ordered_rectangle]
    true_colors_custom_keys =list(true_colors.keys())[0:n_colours]
    # print(true_colors_custom_keys)
    perm = ""
    for col in ordered_colors:
        dist = 1000
        # correct = ''
        for k in true_colors_custom_keys:
            if colorspace == "RGB":
                rgb_summed_diff = abs(k[0]-col[0]) +  abs(k[1]-col[1])  + abs(k[2]-col[2])
                if printing:
                    print(f"K in RGB is {k}")
                    print(f"Col in RGB is {col}")
                    print(f"The summed difference between {k}, and {col} is "+str(rgb_summed_diff) +"\n") 
                new_diff = rgb_summed_diff
            elif colorspace == "HSV":
                k_hsv = colorsys.rgb_to_hsv(k[0]/255, k[1]/255,k[2]/255)
                col_hsv = colorsys.rgb_to_hsv(col[0]/255, col[1]/255,col[2]/255)
                hsv_summed_diff = abs(k_hsv[0]-col_hsv[0]) +  abs(k_hsv[1]-col_hsv[1])  + abs(k_hsv[2]-col_hsv[2])
                if printing:
                    print(f"K in HSV is {k_hsv}")
                    print(f"Col in HSV is {col_hsv}")
                    print(f"The summed difference between {k_hsv}, and {col_hsv} is "+str(hsv_summed_diff) +"\n") 
                new_diff = hsv_summed_diff
            elif colorspace == "CMYK":
                k_cmyk = conv.rgb_to_cmyk(k)
                col_cmyk = conv.rgb_to_cmyk(col)
                cmyk_summed_diff= sum([abs((k_cmyk[0])-(col_cmyk[0])) ,  abs((k_cmyk[1])-(col_cmyk[1]))  , abs((k_cmyk[2])-(col_cmyk[2]))])
                if printing:
                    print(f"K in CMYK is {k_cmyk}")
                    print(f"Col in CMYK is {col_cmyk}")
                    print(f"The summed difference between {k_cmyk}, and {col_cmyk} is "+str(cmyk_summed_diff) +"\n") 
                new_diff = cmyk_summed_diff
            elif colorspace == "LUV":
                k_luv = conv.rgb_to_luv(k)
                col_luv = conv.rgb_to_luv(col)
                a =(int(k_luv[0])-int(col_luv[0]))**2
                b= (int(k_luv[1])-int(col_luv[1]))**2
                c =(int(k_luv[2])-int(col_luv[2]))**2
                pos = a+b+c
                luv_dist= sqrt(pos)
                if printing:
                    print(f"K in LUV is {k_luv}")
                    print(f"Col in LUV is {col_luv}")
                    print(f"The distance between {k_luv}, and {col_luv} is "+str(luv_dist) +"\n") 
                new_diff = luv_dist
            else:
                print("colorspace missing, please provide a choice")
            if new_diff < dist:
                dist = new_diff
                correct = true_colors.get(k)
                if printing:
                    print(new_diff)
                    print(f"the closest correct is {correct}")
        perm += str(correct)
    return (perm)


def get_color_perm_and_dist(ordered_rectangle, n_colours, true_colors,printing:bool = False, colorspace:str = "LUV"):
    ordered_colors = [c[1] for c in ordered_rectangle]
    # print(f"ordered_rectangle: {ordered_rectangle}")
    # print(f"ordered_colors: {ordered_colors}")
    true_colors_custom_keys = list(true_colors.keys())[0:n_colours]
    # print(true_colors_custom_keys)
    # print(true_colors)
    perm = ""
    luv_cols_perm_detected = [conv.rgb_to_luv(col) for col in ordered_colors]
    for col in ordered_colors:
        dist = 1000
        # correct = ''
        for k in true_colors_custom_keys:
                k_luv = conv.rgb_to_luv(k)
                col_luv = conv.rgb_to_luv(col)
                a =(int(k_luv[0])-int(col_luv[0]))**2
                b= (int(k_luv[1])-int(col_luv[1]))**2
                c =(int(k_luv[2])-int(col_luv[2]))**2
                pos = a+b+c
                luv_dist= sqrt(pos)
                if printing:
                    print(f"K in LUV is {k_luv}")
                    print(f"Col in LUV is {col_luv}")
                    print(f"The distance between {k_luv}, and {col_luv} is "+str(luv_dist) +"\n") 
                    print(f"K in RGB is {k}")
                    print(f"Col in RGB is {col}")
                new_diff = luv_dist
                if new_diff < dist:
                    dist = new_diff
                    correct = true_colors.get(k)
                    # print(col)
                    # print(k)
                    # print(correct)
                    if printing:
                        print(new_diff)
                        print(f"the closest correct is {correct}")
        perm += str(correct)
    return (perm,luv_cols_perm_detected)