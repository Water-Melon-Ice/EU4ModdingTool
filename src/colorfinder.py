from PIL import Image
import numpy as np

image = Image.open('terrain.bmp')
width, height = image.size
pixels = image.load()
c = (42,55,22)
for y in range(height):
    for x in range(width):
        if(pixels[x,y] == c):
            print((x,y))