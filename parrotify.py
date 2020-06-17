""" okay this took me like four days to perfect i hate pillow now, its docs
should be clearer,, i s2g it should do much more much more simply half of my
problems were because the save function is so horribly documented. this
function will almost certainly be much simpler in the future
"""

import sys
from PIL import Image
from copy import deepcopy
import numpy as np
# again idk which of the above i actually need its late

FOCUS = [
    [16, 11],
    [12, 10],
    [9, 10],
    [4, 11],
    [4, 12],
    [6, 14],
    [10, 16],
    [15, 14],
    [17, 13],
    [18, 12],
]

def parrot(file_path, out_path):
    """ Convert an image into a parrot.


        Overlays the parrot shape over your image
        Also makes the background transparent
        I'm proud of that because i had to deep
        dive the docs to find that

    """
    im = Image.open('mega_transparent.gif')
    mask = im
    im.seek(0)

    frames = []
    # convert the parrot into an overlay mask
    for index in range(0, im.n_frames):
        im.seek(index)
        im2 = im.convert(mode='RGBA')
        frame = np.array(im2)
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                if frame[i,j,3] >= 200:
                    frame[i,j] = (255,255,255,255)
                else:
                    frame[i,j] = (0, 0, 0, 0)
        tframe = Image.fromarray(frame, mode='RGBA')
        frames.append(tframe)

    im = Image.open('mega_blank_solid.gif')
    out = []
    for i in range(0, 10):
        offset = -(13-FOCUS[i][1])*9+20
        flag = Image.open(file_path)
        flag = flag.convert('RGBA')
        flag = flag.resize((im.width, im.height))
        tflag = deepcopy(flag)
        tflag.paste(flag, (0, offset))
        im.seek(i)
        tflag.paste(im, (0,0), mask=frames[i])
        flag = deepcopy(tflag)
        tflag.paste(flag, (0,0))
        mask = np.array(frames[i])
        image = np.array(tflag)
        for i in range(mask.shape[0]):
            for j in range(mask.shape[1]):
                if mask[i,j,3] > 150:
                    image[i,j,3] = 0
        tflag = Image.fromarray(image, mode='RGBA')
        out.append(tflag)

    out[0].save(out_path, save_all=True, append_images=out[1:], optimize=False, duration=50, loop=0, transparency=0, disposal=2)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        parrot('gq_flag.png', 'gq_parrot.gif')
    elif len(sys.argv) != 3:
        print("Please provide one source file and one destination file")
    else:
        parrot(sys.argv[1], sys.argv[2])
