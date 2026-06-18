import cv2 as cv
import numpy as np
import colorsys

def rgb_to_luv(rgb):
        # print(rgb)
        rgb = np.array([rgb[0], rgb[1], rgb[2]],dtype=np.uint8) # yellow
        rgb = rgb.reshape((1,1,3))
        luv = cv.cvtColor(rgb,cv.COLOR_RGB2Luv)[:,0][0]
        return (int(luv[0]), int(luv[1]), int(luv[2])) if(type(rgb)==tuple) else luv

def luv_to_rgb(luv):
    luv = np.array([luv[0], luv[1], luv[2]],dtype=np.uint8) # yellow
    luv = luv.reshape((1,1,3))
    rgb = cv.cvtColor(luv,cv.COLOR_LUV2RGB)[:,0][0]
    return (int(rgb[0]), int(rgb[1]), int(rgb[2])) if(type(luv)==tuple) else rgb

def rgb_to_cmyk(rgb):
    k = 1 - (max(rgb)/255)
    c = (1 - (rgb[0]/255)-k)/(1-k)
    m = (1 - (rgb[1]/255)-k)/(1-k)
    y = (1 - (rgb[2]/255)-k)/(1-k)
    return (round(c,3),round(m,3),round(y,3),round(k,3)) if type(rgb)==tuple else [round(c,3),round(m,3),round(y,3),round(k,3)]


def cmyk_to_rgb(cmyk):
     r= 255 * (1- cmyk[0]) * (1- cmyk[3])
     g= 255 * (1- cmyk[1]) * (1- cmyk[3])
     b= 255 * (1- cmyk[2]) * (1- cmyk[3])
     return [int(round(r,0)),int(round(g,0)),int(round(b,0))]

def cmyk_to_hsv(cmyk):
    rgb = cmyk_to_rgb(cmyk)
    return colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255,rgb[2]/255)

def rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255,rgb[2]/255)

def hsv_to_rgb(hsv):
    rgb_scaled = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return (round(rgb_scaled[0]*255), round(rgb_scaled[1]*255),round(rgb_scaled[2]*255))