import random
import math
from PIL import Image
import numpy as np
from copy import copy, deepcopy
import time


def generate_noise(width, height, freq = 0, seed = 0):
    np.random.seed(seed)
    perm = list(range(256))
    np.random.shuffle(perm)
    perm += perm
    dirs = [(math.cos(a * 2.0 * math.pi / 256),
            math.sin(a * 2.0 * math.pi / 256))
            for a in range(256)]
    
    def noise(x, y, per):
        def surflet(gridX, gridY):
            distX, distY = abs(x-gridX), abs(y-gridY)
            polyX = 1 - 6*distX**5 + 15*distX**4 - 10*distX**3
            polyY = 1 - 6*distY**5 + 15*distY**4 - 10*distY**3
            hashed = perm[(perm[int(gridX)%per % len(perm)] + int(gridY)%per) % len(perm)]
            grad = (x-gridX)*dirs[hashed][0] + (y-gridY)*dirs[hashed][1]
            return polyX * polyY * grad
        intX, intY = int(x), int(y)
        return (surflet(intX+0, intY+0) + surflet(intX+1, intY+0) +
                surflet(intX+0, intY+1) + surflet(intX+1, intY+1))
                
    def fBm(x, y, per, octs):
        val = 0
        for o in range(octs):
            val += 0.5**o * noise(x*2**o, y*2**o, per*2**o)
        return val
        
    if(freq == 0):
        freq = 1 / ((width + height)/8)
    octs, data = 5, np.zeros((height,width))
    for y in range(height):
        for x in range(width):
            data[y,x] = fBm(x*freq, y*freq, int((width + height) / 2.0 * freq), octs)
    data += 1
    data = data / 2
    return data
    
def generate_landmass(noise, threshold = 0.6):
    height= noise.shape[0]
    width = noise.shape[1]
    landmass = np.zeros((height,width))
    for y in range(noise.shape[0]):
        for x in range(noise.shape[1]):
            point = noise[y,x]
            if point < threshold:
                landmass[y,x] = 0
            else:
                landmass[y,x] = 1
    return landmass
    
def is_point_on_land(x,y, landmass):
    if(landmass[y,x] == 0):
        return False
    return True
    
def color_provinces(landmass,  provincecount = 500):


    def create_new_color(colors, isLand):
        if(isLand):
            choice = np.random.choice(range(256), size=3)
            choice[2] = 0
            c = tuple(choice)
            while c in colors:
                choice = np.random.choice(range(256), size=3)
                choice[2] = 0
                c = tuple(choice)
            colors.append(c)
            return c
        else:
            choice = np.random.choice(range(32), size=3)
            choice[2] = np.random.choice(range(256))
            c = tuple(choice)
            while c in colors:
                choice = np.random.choice(range(32), size=3)
                choice[2] = np.random.choice(range(256))
                c = tuple(choice)
            colors.append(c)
            return c
            
    def generate_points(waterpointscount, landpointscount):
        centers = []
            
        waterpoints = 0
        while waterpoints < waterpointscount:
            y = np.random.randint(0,height)
            x = np.random.randint(0,width)
            if not is_point_on_land(x,y, landmass):
                waterpoints += 1
                centers.append([y,x,create_new_color(colors, False)])
                
        landpoints = 0
        while landpoints < landpointscount:
            y = np.random.randint(0,height)
            x = np.random.randint(0,width)
            if  is_point_on_land(x,y, landmass):
                landpoints += 1
                centers.append([y,x,create_new_color(colors, True)])
                
        return centers

    colors = []
    height= landmass.shape[0]
    width = landmass.shape[1]
    image = Image.new("RGB", (width, height))
    pix = pixels_from_image(image)
    centers = generate_points(provincecount // 10 * 2, provincecount // 10 * 8)
    for y in range(height):
        for x in range(width):
            if(not is_point_on_land(x,y,landmass)):
                mindistance = math.sqrt((y-centers[0][0])**2 + (x-centers[0][1])**2)
                c = 0
                for p in range(1, len(centers)):
                    if(is_point_on_land(centers[p][1], centers[p][0],landmass)):
                        continue
                    distance = math.sqrt((y-centers[p][0])**2 + (x-centers[p][1])**2)
                    if(distance < mindistance):
                        mindistance = distance
                        c = p
                pix[x,y] = centers[c][2]
            if(is_point_on_land(x,y,landmass)):
                mindistance = math.sqrt((y-centers[0][1])**2 + (x-centers[0][0])**2)
                c = 0
                for p in range(1, len(centers)):
                    if(not is_point_on_land(centers[p][1], centers[p][0],landmass)):
                        continue
                    distance = math.sqrt((y-centers[p][0])**2 + (x-centers[p][1])**2)
                    if(distance < mindistance):
                        mindistance = distance
                        c = p
                pix[x,y] = centers[c][2]
        print("Done y= " + str(y))
    return image
    
def generate_rivers(landmass, noise, rivercount = 1000):
    def next_lower(x,y, noise, source):
        xm = 0
        ym = 0
        val = 1.0
        for yi in range(-1,2):
            if(yi + y) < 0:
                continue
            if(yi + y) >= noise.shape[0]:
                continue
                
            for xi in range(-1,2):
                if(xi + x) < 0:
                    continue
                if(xi + x) >= noise.shape[1]:
                    continue
                if (abs(xi) + abs(yi)) > 1:
                    continue
                if (abs(xi) + abs(yi)) == 0:
                    continue
                if(xi+x == source[0]) and ( yi+y == source[1]):
                    continue
                
                if (noise[yi + y,xi + x] <= val):
                    val = noise[yi + y,xi + x]
                    ym = yi
                    xm = xi
        return y+ym, x+xm
    
    def generate_sources(count):
        sources = [] 
        sourcescount = 0
        while sourcescount < count:
            y = np.random.randint(0,height)
            x = np.random.randint(0,width)
            if  is_point_on_land(x,y, landmass):
                sourcescount += 1
                sources.append([y,x])
                
        return sources
                
    height= landmass.shape[0]
    width = landmass.shape[1]
    image = Image.new("RGB", (width, height))
    pix = pixels_from_image(image)   
    points = generate_sources(rivercount)
    for y in range(height):
        for x in range(width):
            if(is_point_on_land(x,y,landmass)):
                pix[x,y] = (255,255,255)
    for i in range(len(points)):
        py, px = points[i]
        pix[px,py] = (0, 255, 0)
        sourceme = (-1,-1)
        source = (px,py)
        sources = []
        sources.append(sourceme)
        sources.append(source)
        while is_point_on_land(px,py,landmass):
            py, px = next_lower(px, py, noise, sourceme)
            if (not pix[px,py] == (0,0,0)) and (not pix[px,py] == (255,255,255)):
                if pix[px,py] == (0, 255, 0):
                    pix[px,py] = (0, 225, 255)
                else:
                    pix[source] = (255, 0, 0)
                    for xfix, yfix in sources:
                        pix[xfix,yfix] = (255,255,255)
                break
            else:
                pix[px,py] = (0, 225, 255)
            sourceme = source
            source = (px,py)
            sources.append(source)
    return image
        

def noise_to_image(noise):
    return Image.fromarray(np.uint8(noise * 255))

def array_from_image(image):
    width, height = im.size
    pixels = pixels_from_image(image)
    array = np.zeros((height,width))
    for y in range(height):
        for x in range(width):
            array[y,x] = pixels[x,y]
    return array
    
def save_image(image, name):
    image.save(name)
    
def open_image(string):
    im = Image.open('whatever.png')
    return im
    
def pixels_from_image(image):
    pix = image.load()
    return pix

def generate_seed():
    seed = int(time.time())
    print(seed)
    return seed



    
if __name__ == "__main__":
    offset = 0.5
    while True:
        offset += 0.001
        seed = 1663529431
        noise = generate_noise(4096//16, 4096//16, seed = seed)
        landmass = generate_landmass(noise, threshold = offset)
        landmass_image = noise_to_image(landmass)
        save_image(landmass_image, str(offset) + "-landmass-" + str(seed) + ".bmp")
        save_image(noise_to_image(noise), str(offset) + "-noise-" + str(seed) + ".bmp")
        
        rivers = generate_rivers(landmass, noise)
        save_image(rivers, str(offset) + "-rivers-" + str(seed) + ".bmp")
        break
    
    
    
    
    
    
    
    
    
    
    
    
    
    