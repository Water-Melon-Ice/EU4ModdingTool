import numpy as np
from PIL import Image, ImagePalette
import sys

def get_palette_list(image):
    palette = image.getpalette()
    return palette

def get_palette_from_file(file):
    return np.load(file)
    
def write_palette_to_file(file, list):
    np.save(file, list)

def reshape_palette(list):
    return list.reshape((-1, 3))
    
def apply_color_table(image, colortable):
    p_img = Image.new('P', image.size)
    p_img.putpalette(colortable.tolist())
    return p_img
    
if __name__ == "__main__":
    # Open image
    im = Image.open(sys.argv[1])

    # Get palette and reshape into 3 columns
    palette = get_palette_list(im)
    write_palette_to_file(sys.argv[1] + ".npy", palette)