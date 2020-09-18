from PIL import Image, ImageChops
import sys
from copy import deepcopy


def rotate(source, destination):
    im = Image.open(source)
    out_images = []
    for frame in range(0, im.n_frames):
        im.seek(frame)
        image = deepcopy(im)
        image = image.rotate(angle=(im.n_frames-frame)*360//im.n_frames)
        out_images.append(image)
    out_images[0].save(destination, save_all=True, append_images=out_images[1:], optimize=True, loop=0, disposal=2)

rotate(sys.argv[1], sys.argv[2])
