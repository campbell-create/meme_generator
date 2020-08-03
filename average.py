import sys
from PIL import Image, ImageChops
from copy import deepcopy
import numpy as np



def average(file1, file2, out_file):
    im1 = Image.open(file1)
    im2 = Image.open(file2)
    alpha = 0.8
    ra = np.array(im1)
    width = ra.shape[0]
    height = ra.shape[1]
    out_images = []
    for index in range(0, im1.n_frames):
        im1.seek(index)
        i1 = np.array(deepcopy(im1).convert('RGBA'))
        i2 = np.array(deepcopy(im2).convert('RGBA'))
        outim = np.zeros(i1.shape, dtype=np.uint8)
        for x in range(width):
            for y in range(height):
                if i1[x, y, 3] < 155 or i2[x, y, 3] < 155:
                    outim[x, y] = [0, 0, 0, 0]
                else:
                    outim[x, y] = [np.uint8(int(c1)*alpha + int(c2)*(1-alpha)) for c1, c2 in zip(i1[x, y], i2[x, y])]
        out_images.append(Image.fromarray(outim).convert('RGB'))

    out_images[0].save(out_file, save_all=True, append_images=out_images[1:], optimize=True, duration=50, loop=0, transparency=0)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Please provide two source files and one destination file")
    else:
        average(sys.argv[1], sys.argv[2], sys.argv[3])

