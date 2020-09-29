""" This was the one that started me on this path.....
    this was too simple and i thought i could do the rest this easily...
"""

from PIL import Image, ImageChops
import sys
from copy import deepcopy


def resize(source, destination, multiplier):
    im = Image.open(source)
    out_images = []
    if isinstance(im, PngImagePlugin.PngImageFile):
        image = im.resize((int(im.width / multiplier), int(im.height / multiplier)))
        image.save(destination)
    else:
        for frame in range(0, im.n_frames):
            im.seek(frame)
            image = deepcopy(im)
            image = image.resize((int(im.width / multiplier), int(im.height / multiplier)))
            out_images.append(image)
        out_images[0].save(destination, save_all=True, append_images=out_images[1:], optimize=True, loop=0, disposal=2)

if len(sys.argv) == 3:
    resize(sys.argv[1], sys.argv[1], float(sys.argv[2]))
elif len(sys.argv) == 4:
    resize(sys.argv[1], sys.argv[2], float(sys.argv[3]))
