import cv2 as cv
import numpy as np
rgb1 = np.array([255, 255, 255],dtype=np.uint8) # yellow
rgb2 = np.array([170, 13, 254],dtype=np.uint8) # amathyst
rgb1 = rgb1.reshape((1,1,3))
rgb2 = rgb2.reshape((1,1,3))
luv1 = cv.cvtColor(rgb1,cv.COLOR_RGB2Luv)
luv2 = cv.cvtColor(rgb2,cv.COLOR_RGB2Luv)
luv3 = np.array([255, 96 ,120], dtype=np.uint8)
luv3 = luv3.reshape((1,1,3))
rgb3 = cv.cvtColor(luv3,cv.COLOR_Luv2RGB)
print("RGB")
print(rgb3)
print(luv1)
print(luv2)
luv1 = luv1.astype(np.float32)
luv2 = luv2.astype(np.float32)

luv_norm1 = (luv1/255)
luv_norm2 = (luv2/255)
luv_r1 = [89.92415 , 22.88858  ,93.96473]
luv_r2 = [46.96060 , 30.26968, -128.8817]
# maxU = 134
# minU = -59
# maxV = 140
# minV = -140

maxU = 220
minU = -134
maxV = 122
minV = -140

# range_of_u_in_r = ((luv_r1[2] -luv_r2[2]) * 255) / (luv1[:,:,2]- luv2[:,:,2])[:,0][0]
# print(range_of_u_in_r)

# max_u_in_r = (255 - luv1[:,:,2]) * range_of_u_in_r / 255
# print(max_u_in_r)

# min_u_in_r = max_u_in_r - range_of_u_in_r
# print(min_u_in_r)

print(luv_norm1[:,:,0]*100, (luv_norm1[:,:,1]*(maxU-minU))+minU,  (luv_norm1[:,:,2]*(maxV-minV))+minV)
print("[89.92415 , 22.88858  ,93.96473] \n")
print(luv_norm2[:,:,0]*100, (luv_norm2[:,:,1]*(maxU-minU))+minU,  (luv_norm2[:,:,2]*(maxV-minV))+minV)
print("46.9 , 30.27, -128.8")
