import sys
from PIL import Image, ImageChops
from copy import deepcopy
import numpy as np

# look if anyone tries to critique my style here i will be upset
# good programming practice is for work and only work
# do you want party reaccs? then dont critique my crap style
# theres comments and thats only because i solved my problems before bedtime

COLORS = [
    0xff8d8b,
    0xfed689,
    0x88ff89,
    0x87ffff,
    0x8bb5fe,
    0xd78cff,
    0xff8cff,
    0xff68f7,
    0xfe6cb7,
    0xff6968,
]

def party(file_path, out_file_path):
    ''' Takes an image and makes it party.

        doesnt read in a gif only a still image.
        i'll figure out gifs later.
        one thing at a time.
        Chris do NOT provide suggestions on how to do gifs.

        just because this produces gifs doesnt mean that it will
        produce gifs *for mattermost*
        you probably will need to resize the image
    '''
    im = Image.open(file_path)
    out_images = []
    for frame in range(0, 10):
        color_image = Image.new('RGBA', (im.height, im.width), COLORS[frame])
        image = ImageChops.multiply(color_image, im)
        out_images.append(image)

    out_images[0].save(out_file_path, save_all=True, append_images=out_images[1:], optimize=True, duration=50, loop=0)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        party('smile_cry.png', 'smile_cry.gif')
    elif len(sys.argv) != 3:
        print("Please provide one source file and one destination file")
    else:
        party(sys.argv[1], sys.argv[2])

