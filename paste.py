import sys
from PIL import Image, ImageChops
from copy import deepcopy
import numpy as np


def paste(file1, file2, out_file, offset=(0,0), scale=1.0):
    """ Put file2 on file1 at offset, scale

        File1 and file2 are both images.
    """
    im1 = Image.open(file1)
    im2 = Image.open(file2)
    width = max(im1.width, im2.width)
    height = max(im1.height, im2.height)
    max_size = (width, height)
    out_image = Image.new('RGBA', max_size, color=(0,0,0,0))
    im1_offset = (width//2-im1.width//2, height//2 - im1.height//2)
    out_image.paste(im1, im1_offset)
    new_size = (int(im2.width * scale), int(im2.height * scale))
    im2 = im2.resize(new_size)
    total_offset = (offset[0]+im1_offset[0], offset[1]+im1_offset[1])
    out_image.paste(im2, total_offset, mask=im2)
    out_image.save(out_file)

if __name__ == '__main__':
    if len(sys.argv) == 7:
        paste(sys.argv[1], sys.argv[2], sys.argv[3], (int(sys.argv[4]), int(sys.argv[5])), float(sys.argv[6]))
    elif len(sys.argv) != 4:
        print("Please provide two source files and one destination file")
    else:
        paste(sys.argv[1], sys.argv[2], sys.argv[3])

