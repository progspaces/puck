from puck.code_modules.helper_functions.helper_functions import clamp
import colorsys
import puck.code_modules.colour_conversion.colour_conversion as conversion
from math import dist

def get_colors_and_coords(point_list, side, image, colorspace):
    def get_dot_list(point_list, side, image):
        dot_list = []
        for pt in point_list:
            x,y= pt
            crop_img = image[clamp(y-side, 0, image.shape[0]):clamp(y+side, 0, image.shape[0]), 
                             clamp(x-side, 0, image.shape[1]): clamp(x+side, 0, image.shape[1])]
            dot_list.append((crop_img, (x,y)))
        return dot_list

    dot_list = get_dot_list(point_list, side, image)

    colors_and_coords = []
    for dot_pair in dot_list:
        dot = dot_pair[0]
        x,y = dot_pair[1]
        maxPixel = (side*2)-1
        corner_points = [dot[0,maxPixel],dot[maxPixel,0],dot[0,maxPixel],dot[maxPixel,maxPixel]]
        if colorspace == "RGB":
            baseline_white_rgb = [max([corner_points[i][0] for i in range(0,4)]),
                            max([corner_points[i][1] for i in range(0,4)]),
                            max([corner_points[i][2] for i in range(0,4)])]
            ## white in this RGB is (255,255,255) so the maximal R G and B are the closest to white you will get
            circle_color= image[y,x]
            # print(f"circle color: {circle_color_rgb}")
            # print(f"baseline white: {baseline_white_rgb}")
            for i in range(len(baseline_white_rgb)):
                if baseline_white_rgb[i] == 0:
                    baseline_white_rgb[i] = 1
            new = [clamp(round(circle_color[0]/baseline_white_rgb[0]*255),0,254),
                   clamp(round(circle_color[1]/baseline_white_rgb[1]*255),0,254),
                   clamp(round(circle_color[2]/baseline_white_rgb[2]*255),0,254)]
        elif colorspace == "HSV":
            corner_points_hsv = [conversion.rgb_to_hsv(p) for p in corner_points]
            baseline_white = [min([corner_points_hsv[i][0] for i in range(0,4)]),
                            min([corner_points_hsv[i][1] for i in range(0,4)]),
                            max([corner_points_hsv[i][2] for i in range(0,4)])]
            if baseline_white[0] ==0:
                baseline_white[0] = 1/179
            if baseline_white[1] ==0:
                baseline_white[1] = 1/255
            circle_color = conversion.rgb_to_hsv(image[y,x])
            # print(hsv_to_rgb(baseline_white))
            # print(f"circle color: {circle_color}")
            # print(f"baseline white: {baseline_white}")
            new = [clamp(round(circle_color[0]/baseline_white[0]*179),0,178)/179,
                   clamp(round(circle_color[1]/baseline_white[1]*255),0,254)/255,
                   clamp(round(circle_color[2]/baseline_white[2]*255),0,254)/255]
            ## When you convert, the white you grab for the white balance is different.
            ## thus the color correction will be different
            ## white in hsv is 0, 0, 100 so min min max
        elif colorspace == "CMYK":
            corner_points_cmyk = [conversion.rgb_to_cmyk(p) for p in corner_points]
            baseline_white = [min([corner_points_cmyk[i][0] for i in range(0,4)]),
                            min([corner_points_cmyk[i][1] for i in range(0,4)]),
                            min([corner_points_cmyk[i][2] for i in range(0,4)]),
                            min([corner_points_cmyk[i][3] for i in range(0,4)]),]
            circle_color = conversion.rgb_to_cmyk(image[y,x])
            # print(f"circle color: {circle_color}")
            # print(f"baseline white: {baseline_white}")
            new = [clamp(round(circle_color[0]-baseline_white[0],3),0,1),
                   clamp(round(circle_color[1]-baseline_white[1],3),0,1),
                   clamp(round(circle_color[2]-baseline_white[2],3),0,1),
                   clamp(round(circle_color[3]-baseline_white[3],3),0,1),]
            ## white in CMYK is 0, 0, 0, 0, so min min min min
        elif colorspace == "LUV":
            corner_points_luv = [conversion.rgb_to_luv(p) for p in corner_points]
            white_rgb = (255,255,255)
            white_luv = conversion.rgb_to_luv(white_rgb)
            min_dist = 10000
            baseline_white = None
            for pt in corner_points_luv:
                if dist(white_luv, pt) < min_dist:
                    min_dist = dist(white_luv, pt)
                    baseline_white = pt
            move = (int(baseline_white[0])-int(white_luv[0]), int(baseline_white[1])-int(white_luv[1]),int(baseline_white[2])-int(white_luv[2]))
            circle_color = conversion.rgb_to_luv(image[y,x])
            new = [clamp(round(int(circle_color[0])- move[0]),0,254),
                   clamp(round(int(circle_color[1])-move[1]),0,254),
                   clamp(round(int(circle_color[2])-move[2]),0,254)]
            # print(f"circle color in rgb pretransform: {image[y,x]}")
            print(f"circle color in luv pretransform: {circle_color}")
            print(f"baseline white: {baseline_white}")
            # print(f"circle color in rgb posttransform: {luv_to_rgb(new)}")
            print(f"circle color in luv posttransform: {new}")
        colors_and_coords.append((dot_pair[1], circle_color))
    return colors_and_coords

## CON

def get_black_dot(colors_and_coords, colorspace):
    colors_and_coords_hsv = []
    for c in colors_and_coords:
        if colorspace == "rgb":
            colors_and_coords_hsv.append((c[0],colorsys.rgb_to_hsv(c[1][0]/255, c[1][1]/255,c[1][2]/255)))
            values = [hsv[1][2] for hsv in colors_and_coords_hsv]
        elif colorspace == "hsv":
            values = [c[1][2] for c in colors_and_coords]
        elif colorspace == "cmyk":
            print(c)
        elif colorspace == "luv":
            # print(c)
            c_rgb = conversion.luv_to_rgb(c[1])
            colors_and_coords_hsv.append((c[0],colorsys.rgb_to_hsv(c_rgb[0]/255, c_rgb[1]/255,c_rgb[2]/255)))
            # print(colors_and_coords_hsv)
            values = [hsv[1][2] for hsv in colors_and_coords_hsv]
            # print(values)
    black_dot = (colors_and_coords[values.index(min(values))])
    return black_dot