import sys
from PIL import Image, ImageChops
from copy import deepcopy
import numpy as np



def append_and_extend(file1, file2, out_file, num1 = 1, num2 = 1):
    """ Append two gifs or images

        If file1 or file2 are an image, this duplicates the image num1 and num2
        times, respectively.
    """
    im1 = Image.open(file1)
    im2 = Image.open(file2)
    out_images = []
    if file1[-3:] == 'gif':
        for index in range(im1.n_frames):
            im1.seek(index)
            out_images.append(im1.convert('RGB'))
    else:
        out_images.extend([im1.convert('RGB') for _ in range(num1)])
    if file2[-3:] == 'gif':
        for index in range(im2.n_frames):
            im2.seek(index)
            out_images.append(im2.convert('RGB'))
    else:
        out_images.extend([im2.convert('RGB') for _ in range(num2)])

    out_images[0].save(out_file, save_all=True, append_images=out_images[1:], optimize=False, disposal=2, duration=int(1000/len(out_images)), loop=0, transparency=0)

if __name__ == '__main__':
    if len(sys.argv) == 6:
        append_and_extend(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif len(sys.argv) != 4:
        print("Please provide two source files and one destination file")
    else:
        append_and_extend(sys.argv[1], sys.argv[2], sys.argv[3])

