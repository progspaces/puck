import cv2 
# from testWebcam import camera 

# camera(False, 10, 1 ,2)

'''
Start with encoding
You get a list of programs.
You assign each of them a unique id.
You use that unique id to get a pattern of 20 dots. five per corner
Four colours is 4^20? 1.0995116e+12 (seems overkill)
Four colours and 4 dots is 4^4 which is only 16
Four colours and 10 dots is 4^10 which is  1,048,576
You store that list of dots as a dataframe for printing
8 colours for david's thing

So let's print 8 colors across the RGB specturm, different sizes, see what it can differentiate

End with Decoding
'''


r g b 