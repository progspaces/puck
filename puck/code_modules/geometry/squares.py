from math import dist
import numpy as np
from puck.code_modules.geometry.rectangles import convertRectToList


def get_dot(rect):
    [a,b,c,_] = convertRectToList(rect)
    vec_ab= np.array(a)-np.array(b)
    vec_ac = np.array(a)-np.array(c) 
    dot = np.dot(vec_ab, vec_ac)
    return dot

def rect_has(rect, dot):
        return dot in convertRectToList(rect)

def get_key_squares(rect_list, keypoint):
    only_relevent_squares = [rect for rect in rect_list if rect_has(rect,keypoint)]
    dot_list = [(get_dot(r),r) for r in only_relevent_squares]
    dot_list.sort(key=lambda x: abs(x[0]))
    square_list = []
    for _,rect, in dot_list:
         [a,b,c,d] = convertRectToList(rect)
         dist_ab = dist(a,b)
         dist_ac = dist(a,c)
         set_version = set([a,b,c,d])
         if (abs(dist_ab-dist_ac) < 15) and len(set_version) == 4:
              square_list.append(rect)
    # print(len(square_list))
    # print(square_list)
    return square_list