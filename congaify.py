""" This was the one that started me on this path.....
    this was too simple and i thought i could do the rest this easily...
"""

from PIL import Image, ImageChops
import sys
from copy import deepcopy


def conga(source, destination, period=40):
    """ Make your parrots/troys/etc conga
        
        source is the original gif
        destination is where you want it
        period is the duration of a given frame
        
        this wont work with a still image
    """ 
    im = Image.open(source)

    out_images = []
    for frame in range(0, im.n_frames):
        im.seek(frame)
        image = deepcopy(im)
        image = ImageChops.offset(image, frame*im.width//(im.n_frames), yoffset=0)
        out_images.append(image)
    out_images[0].save(destination, save_all=True, append_images=out_images[1:], optimize=True, duration=period, loop=0, disposal=2)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        conga('mega_blank_solid.gif', 'conga_parrot.gif')
    elif len(sys.argv) == 3:
        conga(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        conga(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Please provide one source file and one destination file, optionally a frametime")
