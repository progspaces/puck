import plotly.express as px
import pandas as pd
import puck.code_modules.colour_conversion.colour_conversion as conv



points = [[129, 124, 124],
 [ 92, 130, 122],
[107, 132, 123],
 [ 98, 130, 119],
[143, 123, 124],
 [143, 123, 124],
[113, 138, 119],
[ 99, 132, 118],
[104, 135, 121],
[140, 121, 114],
[124, 124, 118],
 [129, 137, 126],
 [ 99, 129, 124],
 [106, 128, 123],
 [ 87, 126, 124],
[ 87, 126, 124],
[ 95, 123, 122]]

x = [p[0] for p in points]
y = [p[1] for p in points]
z= [p[2] for p in points]
classification = ["col"]*len(points)

b_rgb= [134, 60, 123]
b_luv =conv.rgb_to_luv(b_rgb)
f_rgb = [153, 25, 84]
f_luv =conv.rgb_to_luv(f_rgb)
print(b_luv, f_luv)

data = pd.DataFrame({"x":x,"y":y,"z":z, "class":classification})
data.loc[len(data)]=({"x":b_luv[0], "y":b_luv[1], "z": b_luv[2], "class": "b"})
data.loc[len(data)]=({"x":f_luv[0], "y":f_luv[1], "z": f_luv[2], "class": "f"})

x.append(b_luv[0])
x.append(f_luv[0])

y.append(b_luv[1])
y.append(f_luv[1])

z.append(b_luv[2])
z.append(f_luv[2])

colour_list = ['rgb(200, 200, 200)'] *17
for i in range(0,1):
    colour_list.append('rgb(255, 0, 255)')
for i in range(0,1):
    colour_list.append('rgb(219, 79, 137)')
# print(colour_list)
print(len(colour_list))
print(len(x))

fig = px.scatter_3d(x=x, y=y, z=z, color = colour_list, color_discrete_sequence=['rgb(200, 200, 200)','rgb(255,0,255)','rgb(219, 79, 137)',])
fig.update_traces(marker_size = 13)

fig.update_layout(scene = dict(
                    xaxis = dict(
                         gridcolor="white",
                         showbackground=True,
                         gridwidth=10,
                         zerolinecolor="white",),
                    yaxis = dict(
                        gridcolor="white",
                        showbackground=True,
                        gridwidth=10,
                        zerolinecolor="white"),
                    zaxis = dict(
                        gridcolor="white",
                        gridwidth=10,
                        showbackground=True,
                        zerolinecolor="white",),),
                  )
fig.show() 