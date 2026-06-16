import puck.code_modules.geometry.rectangles as rect
import puck.code_modules.geometry.clockwise_dots as clkwise
import puck.code_modules.geometry.squares as squares


from math import dist

def small_big(rect_list, keypoint):
    square_list = squares.get_key_squares(rect_list, keypoint)
    if len(square_list) != 2:
        print("You have an empty list or too many squares, either way something is wrong!")
        print(square_list)
        print("EXITING")
        return 
    square0 = square_list[0]
    square1 = square_list[1]
    [a0,b0,_,_] = rect.convertRectToList(square0)
    [a1,b1,_,_] = rect.convertRectToList(square1)
    dist0 = dist(a0,b0)
    dist1 = dist(a1,b1)
    if dist0 > dist1:
        small = square1
        big = square0
    else:
        small = square0
        big = square1
    return (small,big)


def get_calibration_colors(black_dot_coords, color_coord_list, n_colours):
    coord_list = [c[0] for c in color_coord_list]
    small, big = small_big(rect.check_rects(coord_list),black_dot_coords)
    small_list = rect.convertRectToList(small)
    big_list = rect.convertRectToList(big)
    calibration_order_list = [()] * 8
    if (black_dot_coords not in small_list) or (black_dot_coords not in big_list):
        print("Black Dot Not in at least one squares given, something is wrong!")
        return
    a = clkwise.clockwise_pt(small_list, black_dot_coords)
    calibration_order_list[0] = a
    d = clkwise.clockwise_pt(small_list, a)
    calibration_order_list[3] = d
    c = clkwise.clockwise_pt(small_list, d)
    calibration_order_list[2] = c
    b = clkwise.clockwise_pt(big_list, black_dot_coords)
    calibration_order_list[1]= b
    h = clkwise.clockwise_pt(big_list, b)
    calibration_order_list[7] = h
    f = clkwise.clockwise_pt(big_list, h)
    calibration_order_list[5] = f
    colored = [c for c in coord_list if c is not black_dot_coords]
    remaining = [ c for c in colored if c not in calibration_order_list]
    slope_fh = (f[1]-h[1]) / (f[0]-h[0])
    opt_1 = remaining[0]
    opt_2 = remaining[1]
    # print(len(colored))
    slope_f1 = (f[1]-opt_1[1]) / (f[0]-opt_1[0])
    slope_f2 = (f[1]-opt_2[1]) / (f[0]-opt_2[0])
    # print(f"abs(slope_fh - slope_f1)  {abs(slope_fh - slope_f1) }")
    # print(f"abs(slope_fh - slope_f2)  {abs(slope_fh - slope_f2) }")
    if abs(slope_fh - slope_f1) < abs(slope_fh - slope_f2):
        # print(f" abs(slope_fh - slope_f1) < abs(slope_fh - slope_f2) so g is ")
        calibration_order_list[6] = opt_1
        calibration_order_list[4] = opt_2
    else:
        calibration_order_list[4] = opt_1
        calibration_order_list[6] =opt_2
    calibration_order_list.insert(0,black_dot_coords)
    colored_coord_list = [c for c in color_coord_list if c[0] is not black_dot_coords]
    colors_sorted = sorted(colored_coord_list, key = lambda x: calibration_order_list.index(x[0]))
    colors = [c[1] for c in colors_sorted]
    # print(colors)
    indicies = range(0,9)
    color_dict = {}
    for i in range(n_colours):
        r,g,b = colors[i]
        color_dict.update({ (int(r),int(g),int(b)):indicies[i]})
    print(color_dict)
    return color_dict

