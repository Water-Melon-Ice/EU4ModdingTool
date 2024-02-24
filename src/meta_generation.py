import map_generation as mg
import province_name_generation as prov
import colourtable as ct
import numpy as np
from PIL import Image
import shutil
import time
import os

def create_definition_csv(provinces_image):
    colors = province_colors(provinces_image)
    with open("mod/definition.csv", "w") as file:
        file.write("province;red;green;blue;x;x\n")
        for c in range(len(colors)):
            file.write(str(c + 1) + ";")#provinceID
            file.write(str(colors[c][0]) + ";")#red
            file.write(str(colors[c][1]) + ";")#green
            file.write(str(colors[c][2]) + ";")#blue
            file.write(str(generate_name(colors[c][2])) + ";")#name
            file.write("x\n")#x

def is_sea_province(blue):
    if(blue == 0):
        return False
    return True

def generate_name(blue):
    if(is_sea_province(blue)):
        return generate_sea_name() + " Sea"
    else:
        return generate_province_name()

def generate_province_name():
    return prov.create_name("KAAAAL")
    
def generate_sea_name():
    return prov.create_name("KAAAA")
    
def get_sea_province_IDs():
    ids = []
    with open("mod/definition.csv") as file:
        next(file)
        for line in file:
            parts = line.split(";")
            id = parts[0]
            b = int(parts[3])
            if(is_sea_province(b)):
                ids.append(id)
    return ids

def get_land_province_IDs():
    ids = []
    with open("mod/definition.csv") as file:
        next(file)
        for line in file:
            parts = line.split(";")
            id = parts[0]
            b = int(parts[3])
            if(not is_sea_province(b)):
                ids.append(id)
    return ids

def create_default_map(noise_image, landmass_image, provinces_image, rivers_image):
    with open("mod/default.map", "w") as file:
        width, height = noise_image.size
        max_provinces = len(province_colors(provinces_image))
        file.write(f"width = {width}\n")
        file.write(f"height = {height}\n")
        file.write("max_provinces  = 32768\n\n")
        file.write("sea_starts  = {" + " ".join(get_sea_province_IDs()) +"}\n")
        
        with open("default.map.txt") as txt:
            lines = txt.readlines()
            for line in lines:
               file.write(line)

def create_terrain_txt():
    with open("mod/terrain.txt", "w") as file:
        with open("terrain.txt.txt") as txt:
            lines = txt.readlines()
            for line in lines:
               file.write(line)
               
def create_area_txt():
    with open("mod/area.txt", "w") as file:
        sea_area_names = []
        seaprovinces = get_sea_province_IDs()
        spiter = iter(seaprovinces)
        val = next(spiter, None)
        while val != None:
            gsn = generate_sea_name() + "_sea_area"
            while gsn in sea_area_names:
                gsn = generate_sea_name() + "_sea_area"
            sea_area_names.append(gsn)
            file.write(gsn + " = {\n ")
            for i in range(np.random.randint(5,16)):
                if(val == None):
                    break
                else:
                     file.write(val)
                     file.write(" ")
                val = next(spiter, None)
            file.write("\n}\n\n")
        
        land_area_names = []
        landprovinces = get_land_province_IDs()
        spiter = iter(landprovinces)
        val = next(spiter, None)
        while val != None:
            gpn = generate_province_name() + "_area"
            while gpn in land_area_names:
                gpn = generate_province_name() + "_area"
            land_area_names.append(gpn)
            file.write(gpn + " = {\n ")
            for i in range(np.random.randint(3,8)):
                if(val == None):
                    break
                else:
                    file.write(val)  
                    file.write(" ")
                val = next(spiter, None)
            file.write("\n}\n\n")
        return sea_area_names, land_area_names

def create_regions_txt(sea_area_names, land_area_names):
    with open("mod/region.txt", "w") as file:
        seaprovinces = get_sea_province_IDs()
        spiter = iter(sea_area_names)
        val = next(spiter, None)
        while val != None:
            gsr = generate_province_name() + "_sea_region"
            file.write(gsr + " = {\n areas = {\n ")
            for i in range(np.random.randint(5,16)):
                if(val == None):
                    break
                else:
                     file.write(val)
                     file.write("\n ")
                val = next(spiter, None)
            file.write("}\n}\n\n")
        
        region_names = []
        spiter = iter(land_area_names)
        val = next(spiter, None)
        while val != None:
            file.write("\n")
            gr = generate_province_name() + "_region"
            region_names.append(gr)
            file.write(gr + " = {\n areas = {\n ")
            for i in range(np.random.randint(5,10)):
                if(val == None):
                    break
                else:
                     file.write(val)
                     file.write("\n ")
                val = next(spiter, None)
            file.write("}\n}\n\n")
        return region_names

def create_superregions_txt(region_names):
    with open("mod/superregion.txt", "w") as file:
        spiter = iter(region_names)
        val = next(spiter, None)
        while val != None:
            gsr = generate_province_name() + "_superregion"
            file.write(gsr + " = {\n")
            for i in range(np.random.randint(3,6)):
                if(val == None):
                    break
                else:
                     file.write(" " + val)
                     file.write("\n")
                val = next(spiter, None)
            file.write("}\n\n")

def province_colors(provinces_image):
    width, height = provinces_image.size
    colors = provinces_image.getcolors(maxcolors=width * height)
    if(colors != None):
        return [c[1] for c in colors]
    else:
        print("Did not find province colors. Collecting...")
        colors = []
    pix = provinces_image.load()
    for y in range(height):
        for x in range(width):
            if(not pix[x,y] in colors):
                colors.append(pix[x,y])
    return colors

if(__name__ == "__main__"):
    
    
    seed = time.time_ns() // 1_000_000_000
    
    modfolder = "mod/"
    if not os.path.exists(modfolder):
        os.mkdir(modfolder)
    
    mapfolder = modfolder + "map/"
    if not os.path.exists(mapfolder):
        os.mkdir(mapfolder)
    
    noise_image_path = "heightmap.bmp"
    if not os.path.exists(mapfolder + noise_image_path):
        print("generating Noise")
        noise = mg.generate_noise(4096, 4096, seed = seed)
        noise_image = mg.noise_to_image(noise)
        mg.save_image(noise_image, noise_image_path)
    else:
        print("Noise found. Loading...")
        noise_image = mg.open_image(mapfolder + noise_image_path)
        noise = mg.array_from_image(noise_image)
    
    landmass_image_path = "landmass.bmp"
    if not os.path.exists(mapfolder + landmass_image_path):
        print("generating Landmass")
        landmass = mg.generate_landmass(noise, threshold = 0.6)
        landmass_image = mg.noise_to_image(landmass)
        mg.save_image(landmass_image, landmass_image_path)
    else:
        print("Landmass found. Loading...")
        landmass_image = mg.open_image(mapfolder + landmass_image_path)
        landmass = mg.array_from_image(landmass_image)
    
    provinces_image_path = "provinces.bmp"
    if not os.path.exists(mapfolder + provinces_image_path):
        print("generating Provinces")
        provinces_image = mg.color_provinces(landmass)
        mg.save_image(provinces_image, provinces_image_path)
    else:
        print("Provinces found. Loading...")
        provinces_image = mg.open_image(mapfolder + provinces_image_path)
    
    rivers_image_path = "rivers.bmp"
    if not os.path.exists(mapfolder + rivers_image_path):
        print("generating Rivers")
        rivers_image = mg.generate_rivers(landmass, noise)
        mg.save_image(rivers_image, rivers_image_path)
    else:
        print("Rivers found. Loading...")
        rivers_image = mg.open_image(mapfolder + rivers_image_path)
    
    terrain_image_path = "terrain.bmp"
    if not os.path.exists(mapfolder + terrain_image_path):
        print("generating Terrain")
        terrain = mg.generate_terrain(noise, landmass, rivers_image)
        mg.save_image(terrain, terrain_image_path)
    else:
        print("Terrain found. Loading...")
        terrain = mg.open_image(mapfolder + terrain_image_path)
    
    create_terrain_txt()
    
    definition_csv_path = "definition.csv"
    if not os.path.exists(mapfolder + definition_csv_path):
        print("generating definition.csv")
        create_definition_csv(provinces_image)
    else:
        print("definition.csv found. Loading...")
        
    default_map_path = "default.map"
    if not os.path.exists(mapfolder + default_map_path):
        print("generating default.map")
        create_default_map(noise_image, landmass_image, provinces_image, rivers_image)
    else:
        print("default.map found. Loading...")
        
    if not os.path.exists(mapfolder + "area.txt"):
        print("generating area.txt")
        sea_area_names, land_area_names = create_area_txt()
        print("generating region.txt")
        region_names = create_regions_txt(sea_area_names, land_area_names)
        print("generating superregion.txt")
        create_superregions_txt(region_names)
    else:
        print("area.txt found. Not Checking for region.txt and superregion.txt")
        
    trees_image_path = "trees.bmp"
    trees_palette_path = "trees.bmp.npy"
    if not os.path.exists(mapfolder + trees_image_path):
        print("generating trees.bmp")
        if not os.path.exists(trees_palette_path):
            print("ERROR: trees.bmp.npy not found.")
        else:
            print("found trees.bmp.npy")
            trees_image = mg.generate_trees(landmass)
            mg.save_image(trees_image, trees_image_path)
    else:
        print("Trees.bmp found. Not Checking for region.txt and superregion.txt")