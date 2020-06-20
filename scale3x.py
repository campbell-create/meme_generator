""" Implements Scale3x/AdvMAME3x scaling algorithm as described in the below link.
    https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms#Scale3%C3%97/AdvMAME3%C3%97_and_ScaleFX
    Why did I choose this one? looked easy
"""
import sys
from PIL import Image
import numpy as np
from copy import deepcopy

def scale3x(in_image = None, in_path = None, out_path = None):
    """ Scales an image 3x.

        Input image can either be a path or a pillow Image.
        out_path is an optional argument and if it's specified the image will be written there.
    """
    if in_path and not in_image:
        im = Image.open(in_path)
        image = im.convert(mode='RGBA')
    elif in_image and not in_path:
        image = in_image
    else:
        print("Requires exactly one of in_image and in_path. Exiting")
        sys.exit(1)

    orig = np.array(image)
    shape = list(orig.shape)
    shape[0] = shape[0]*3
    shape[1] = shape[1]*3
    print(shape)
    shape = tuple(shape)
    print(shape)
    out_image = np.zeros(shape, dtype=np.uint8)
    print(type(out_image))
    print(out_image.shape)
    for i in range(orig.shape[0]):
        for j in range(orig.shape[1]):
            for a in range(0, 3):
                for b in range(0, 3):
                    x = i*3+a
                    y = j*3+b
                    out_image[x][y] = orig[i][j]

    out_image = Image.fromarray(out_image, mode='RGBA')
    if out_path:
        out_image.save(out_path)

    return out_image


if __name__ == '__main__':
    scale3x(in_path='parrot.gif', out_path='bigger_parrot.png')
