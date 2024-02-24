import random
import math
from PIL import Image
import numpy as np
from copy import copy, deepcopy
import time
import colourtable
import sys
from scipy.spatial import distance

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
        print("Done noise y = " + str(y))
    data += 1
    data = data / 2
    return data
            
    
def generate_landmass(noise, threshold = 0.6):
    height= noise.shape[0]
    width = noise.shape[1]
    landmass = np.zeros((height,width))
    for y in range(height):
        for x in range(width):
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

def get_height_at(x,y,noise):
    return noise[y,x]
    
def is_point_bordering_land(x,y, landmass):
    height= landmass.shape[0]
    width = landmass.shape[1]
    if(is_point_on_land(x,y, landmass)):
        return False
    if(x+1 < width):
        if(landmass[y,x+1] == 1):
            return True
    if(x-1 >= 0):        
        if(landmass[y,x-1] == 1):
            return True
    if(y+1 < height):   
        if(landmass[y+1,x] == 1):
            return True
    if(y-1 >= 0):
        if(landmass[y-1,x] == 1):
            return True
    return False
    
def get_all_points_on_land(landmass):
    height= landmass.shape[0]
    width = landmass.shape[1]
    points = []
    for y in range(height):
        for x in range(width):
            if(landmass[y,x] == 1):
                points.append([y,x])
    return points
    
def get_all_points_bordering_land(landmass):
    height= landmass.shape[0]
    width = landmass.shape[1]
    points = []
    for y in range(height):
        for x in range(width):
            if(is_point_bordering_land(x,y,landmass)):
                points.append([y,x])
    return points
    
    
def color_provinces(landmass,  provincecount = None):   

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
        else:
            choice = np.random.choice(range(32), size=3)
            choice[2] = np.random.choice(range(1, 256))
            c = tuple(choice)
            while c in colors:
                choice = np.random.choice(range(32), size=3)
                choice[2] = np.random.choice(range(256))
                c = tuple(choice)
            colors.append(c)
        if(c[0] == 0 and c[1] == 0 and c[2] == 0):
            return create_new_color(colors, isLand)
        return c
            
    def generate_points(waterpointscount, landpointscount):
            
        waterpoints = 0
        centers = []
        colors = []
        while waterpoints < waterpointscount:
            y = np.random.randint(0,height)
            x = np.random.randint(0,width)
            if not is_point_on_land(x,y, landmass):
                waterpoints += 1
                centers.append([y,x])
                colors.append(create_new_color(colors, False))
                
        landpoints = 0
        landcenters = []
        landcolors = []
        while landpoints < landpointscount:
            y = np.random.randint(0,height)
            x = np.random.randint(0,width)
            if  is_point_on_land(x,y, landmass):
                landpoints += 1
                landcenters.append([y,x])
                landcolors.append(create_new_color(colors, True))
                
        return landcenters, landcolors, centers, colors
    
    def closest_node(node, nodes):
        closest_index = distance.cdist([node], nodes).argmin()
        return closest_index

    colors = []
    height= landmass.shape[0]
    width = landmass.shape[1]
    
    if(provincecount == None):
        provincecount = ((height/32) * (width/32))
    
    image = Image.new("RGB", (width, height))
    pix = pixels_from_image(image)
    landcenters, landcolors, centers, colors = generate_points(provincecount // 10 * 2, provincecount // 10 * 8)
    for y in range(height):
        for x in range(width):
            if(not is_point_on_land(x,y,landmass)):
                closest_index = closest_node((y,x), centers)
                pix[x,y] = colors[closest_index]
                
                
            if(is_point_on_land(x,y,landmass)):
                closest_index = closest_node((y,x), landcenters)
                pix[x,y] = landcolors[closest_index]
        print("Done provincemap y = " + str(y))
    return image
    
def next_higher(x,y, noise, source):
    xm = 0
    ym = 0
    val = get_height_at(x,y,noise)
    diff = 0.0
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
            
            point = (yi + y,xi + x)
            
            if (noise[point] > val and (noise[point]-val) >= diff):
                diff = noise[point] - val
                ym = yi
                xm = xi
    if(ym == 0 and xm == 0):
        return -1, -1
    return y+ym, x+xm

rivercolors = [(255,252,0), (255,0,0), (0,225,255), (0,255,0)]

def generate_river(px,py, pix, noise):
    pix_flow_out_source = rivercolors[0]
    pix_flow_in_source = rivercolors[1]
    pix_flow = rivercolors[2]
    pix_source = rivercolors[3]
    source = (px,py)
    pix[source] = pix_flow
    sourceme = (-1,-1)
    sources = []
    sources.append(sourceme)
    sources.append(source)
    while (not py == -1 and not px == -1):
        py, px = next_higher(px, py, noise, sourceme)
        if(py == -1 or px == -1):
            pix[source] = pix_source
            break
        if((px,py) in sources):
            pix[source] = pix_source
            break
        if(pix[px,py] == pix_flow):
            pix[source] = pix_flow_out_source
            break
        if(pix[px,py] == pix_source):
            pix[source] = pix_source
            break
        pix[px,py] = (0, 225, 255)
        sourceme = source
        source = (px,py)
        sources.append(source)

    
def generate_rivers(landmass, noise, rivercount = 100):
    
    def generate_sources(count):
        sources = [] 
        sourcescount = 0
        possiblePoints = get_all_points_bordering_land(landmass)
        while sourcescount < count:
            index = np.random.randint(0,len(possiblePoints))
            a = possiblePoints[index]
            if  is_point_bordering_land(a[1],a[0], landmass):
                sourcescount += 1
                sources.append(a)
                possiblePoints.pop(index)
                
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
            else:
                pix[x,y] = (122,122,122)
    for i in range(len(points)):
        py, px = points[i]
        generate_river(px,py, pix, noise)
        
    image = apply_color_table(image, colourtable.get_color_table_from_file("rivers.bmp.txt"))
    return image
    
def generate_terrain(noise, landmass, rivers):
    height= landmass.shape[0]
    width = landmass.shape[1]
    
    grasslands = 0
    hills = 1
    desert = 3
    steppe = plains = 4
    drylands = 5
    mountain = 6
    marsh = 9
    farmlands = 10 # Maybe farmlands, called terrain_10 in terrain.txt
    ocean = 15
    snow = 16#special
    inland_ocean = 17
    glacier = 18
    coastal_desert = 19
    coastline = 35
    forest = 13
    woods = 255
    jungle = 254#white
    highlands = 23
    savannah = 20
    
    desert_mountain_2 = 2    
    desert_mountain_high_7 = 7
    desert_mountain_low_8 = 8
    terrain_11 = 11
    forest_12 = 12
    forest_14 = 14
    savannah_20 = 20
    drylands_22 = 22
    dry_highlands_24 = 24
    woods_255 = 255
    terrain_21 = 21
    
    water_height = 0.6
    hills_min_height = water_height + 0.2
    highlands_min_height = hills_min_height + 0.08
    mountain_min_height = hills_min_height + 0.05
    ice_min_height = mountain_min_height + 0.03
    marsh_max_height = 0.6001
    tropics_min_y = 0.4
    tropics_max_y = 0.6
    subtropics_min_y = 0.3
    subtropics_max_y = 0.7
    temperate_min_y = 0.1
    temperate_max_y = 0.9
    
    zones_factor = height * 0.03
    
    farmlands_river_distance = height // 64
    inland_ocean_coast_distance = height // 32
    grasslands_coast_distance = height // 32
        
    def get_distance_to_coast(x,y, landmass):
        height= landmass.shape[0]
        width = landmass.shape[1]
        test_for_land_or_water = 0 if landmass[y,x] == 1 else 1
        for i in range(max(width,height)):
            for yp in range(y-i,y+i+1):
                if(yp < 0 or yp >= height):
                    continue
                for xp in range(x-i,x+i+1):
                    if(xp < 0 or xp >= width):
                        continue
                    if(landmass[yp,xp] == test_for_land_or_water):
                        return i
                        
    def get_distance_to_river(x,y, rivers, distance):
        riverp = rivers.load()
        width, height = rivers.size
        for i in range(distance):
            for yp in range(y-i,y+i+1):
                if(yp < 0 or yp >= height):
                    continue
                for xp in range(x-i,x+i+1):
                    if(xp < 0 or xp >= width):
                        continue
                    if(abs(yp-y)+abs(xp-x) < 2*i-2):
                        continue
                    if(riverp[xp,yp] in rivercolors):
                        return i
        return -1
                    
    def get_terrain(x,y,noise,landmass, rivers):
        return snow
        
        if(noise[y,x] >= ice_min_height):#Permanent Snow
            return snow
        if(noise[y,x] >= mountain_min_height):#Mountain
            return mountain
        if(noise[y,x] >= highlands_min_height):#Highlands
            return highlands
        if(noise[y,x] >= hills_min_height):#Hills
            return hills
        distance_to_coast = get_distance_to_coast(x,y,landmass)
        if(landmass[y,x] == 0):
            if(distance_to_coast <= inland_ocean_coast_distance and noise[y,x] > 0.6 * water_height):
                return inland_ocean #Inland Ocean
            else:
                return ocean #Ocean
        height= landmass.shape[0]
        distance_to_river = get_distance_to_river(x,y,rivers, farmlands_river_distance)
        if(distance_to_river <= farmlands_river_distance and distance_to_river != -1):
            return farmlands #Farmlands
        if(distance_to_coast <= 1):
            return coastline #Coastline
        
        if(y in range(int(height*tropics_min_y + random.uniform(-zones_factor, zones_factor)), int(height*tropics_max_y + random.uniform(-zones_factor, zones_factor)))):
            #desert and coastal desert
            if(distance_to_coast <= grasslands_coast_distance):
                return coastal_desert#Coastal Desert
            return desert
        if(y in range(int(height*subtropics_min_y + random.uniform(-zones_factor, zones_factor)), int(height*subtropics_max_y + random.uniform(-zones_factor, zones_factor)))):
            #drylands and steppe and savannah and jungle
            if(distance_to_coast <= grasslands_coast_distance):
                return jungle
            elif(distance_to_coast <= grasslands_coast_distance * 2):
                return savannah
            elif(distance_to_coast <= grasslands_coast_distance * 3):
                return drylands
            else:
                return steppe
        if(y in range(int(height*temperate_min_y + random.uniform(-zones_factor, zones_factor)), int(height*temperate_max_y + random.uniform(-zones_factor, zones_factor)))):
            #woods and steppe and grassland and marsh
            if(noise[y,x] <= marsh_max_height + random.uniform(-0.15, 0.01)):
                return marsh
            if(distance_to_coast <= grasslands_coast_distance):
                return grasslands
            elif(distance_to_coast <= grasslands_coast_distance * 3):
                return woods
            else:
                return steppe
        else:
            #forest and glacier
            if(distance_to_coast <= grasslands_coast_distance):
                return glacier
            else:
                return forest
            return
        
        #Missing: Woods, Forest, Savannah, Jungle, Marsh, Drylands, Highlands
        
    image = Image.new("RGB", (width, height))
    palette_list = colourtable.get_palette_from_file("terrain.bmp.npy")
    palette = colourtable.reshape_palette(palette_list)
    image = colourtable.apply_color_table(image, colourtable.get_palette_from_file("terrain.bmp.npy"))
    pix = pixels_from_image(image)
    for y in range(height):
        for x in range(width):
            pix[x,y] = get_terrain(x,y,noise,landmass, rivers)
        print("Done terrainmap y = " + str(y))
    return image
    
def generate_trees(landmass):
    palette_indices = [3, 4, 9, 10]
    height= landmass.shape[0]
    width = landmass.shape[1]
    def get_tree(x,y):
        if(height//2 - height//4 < y < height//2 + height//4):
            return random.choice((palette_indices[2], palette_indices[3]))
        else:
            return random.choice((palette_indices[0], palette_indices[0]))

    points = get_all_points_on_land(landmass)
    image = Image.new("RGB", (width, height))
    image = colourtable.apply_color_table(image, colourtable.get_palette_from_file("trees.bmp.npy"))
    pix = pixels_from_image(image)
    palette_list = colourtable.get_palette_from_file("trees.bmp.npy")
    palette = colourtable.reshape_palette(palette_list)
    print("Placing n-Trees: " + str(len(points))) 
    for pt in points:
        pix[pt[0], pt[1]] = get_tree(pt[0], pt[1])
    return image

def noise_to_image(noise):
    return Image.fromarray(np.uint8(noise * 255))

def array_from_image(image):
    width, height = image.size
    pixels = pixels_from_image(image)
    array = np.zeros((height,width))
    for y in range(height):
        for x in range(width):
            array[y,x] = pixels[x,y]//255
    return array
    
def save_image(image, name):
    image.save("mod/"+name)
    
def open_image(string):
    im = Image.open(string)
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
        seed = 1664229506#time.time_ns() // 1_000_000_000
        
        print("generating Noise")
        noise = generate_noise(4096, 4096, seed = seed)
        save_image(noise_to_image(noise), str(offset) + "-noise-" + str(seed) + ".bmp")
        
        print("generating Landmass")
        landmass = generate_landmass(noise, threshold = offset)
        landmass_image = noise_to_image(landmass)
        save_image(landmass_image, str(offset) + "-landmass-" + str(seed) + ".bmp")
        
        print("generating Provinces")
        provinces = color_provinces(landmass, provincecount = 4096)
        save_image(provinces, str(offset) + "-provinces-" + str(seed) + ".bmp")
        
        print("generating Rivers")
        rivers = generate_rivers(landmass, noise)
        save_image(rivers, str(offset) + "-rivers-" + str(seed) + ".bmp")
        
        #print("generating Terrain")
        #terrain = generate_terrain(noise, landmass, rivers)
        #save_image(terrain, str(offset) + "-terrain-" + str(seed) + ".bmp")
        
        break
    
    
    
    
    
    
    
    
    
    
    
    
    