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

def parrot(file_path, out_path, x_delta=0, y_delta=0):
    """ Convert an image into a parrot.


        Overlays the parrot shape over your image
        Also makes the background transparent
        I'm proud of that because i had to deep
        dive the docs to find that

    """
    im = Image.open('data/mega_transparent.gif')

    frames = []
    # convert the parrot into an overlay mask
    # but we're also going to shrink the black region slightly
    # using "advanced computer vision algorithms"
    for index in range(0, im.n_frames):
        im.seek(index)
        im2 = im.convert(mode='RGBA')
        frame = np.array(im2)
        original = deepcopy(frame)
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                # now we're going to see if neighbor pixels
                # are mostly transparent(T) or opaque (o)
                # if mostly T, then this pixel is T
                # and o if theyre mostly o
                # this would normally be a convolution but im interested
                # in preserving alpha values and im not thinking too much rn
                thresh = 255
                if i > 1:
                    left = original[i-1, j, 3] < thresh
                else:
                    left = False
                if i < frame.shape[0]-1:
                    right = original[i+1, j, 3] < thresh
                else:
                    right = False
                if j > 1: 
                    upper = original[i, j-1, 3] < thresh
                else:
                    upper = False
                if j < frame.shape[1]-1:
                    lower = original[i, j+1, 3] < thresh
                else:
                    lower = False
                curr = original[i, j, 3] < thresh
                if left and right and upper and lower and curr:
                    frame[i,j] = (0, 0, 0, 0)
                else:
                    frame[i,j] = (255,255,255,255)
        original = deepcopy(frame) # update "constant" frame
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                thresh = 255
                if i > 1:
                    left = original[i-1, j, 3] < thresh
                else:
                    left = False
                if i < frame.shape[0]-1:
                    right = original[i+1, j, 3] < thresh
                else:
                    right = False
                if j > 1: 
                    upper = original[i, j-1, 3] < thresh
                else:
                    upper = False
                if j < frame.shape[1]-1:
                    lower = original[i, j+1, 3] < thresh
                else:
                    lower = False
                curr = original[i, j, 3] < thresh
                #print(int(left + right + upper + lower + curr))
                if left or right or upper or lower or curr:
                    #if int(left + right + upper + lower + curr) > 2:
                    frame[i,j] = (0, 0, 0, 0)
                else:
                    frame[i,j] = (255, 255, 255, 255)
        tframe = Image.fromarray(frame, mode='RGBA')
        frames.append(tframe)
        if index < 1:
            tframe.save('frame.png')

    im = Image.open('data/mega_blank_solid.gif')
    out = []
    for i in range(0, 10):
        x, y = FOCUS[i]
        y_offset = -(13-y)*9+20+y_delta
        x_offset = x*9-90+x_delta
        flag = Image.open(file_path)
        flag = flag.convert('RGBA')
        flag = flag.resize((im.width, im.height))
        tflag = deepcopy(flag)
        tflag.paste(flag, (x_offset, y_offset))
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
    # this is complicated enough its almost ready to argparse
    if len(sys.argv) == 1:
        parrot('data/gq_flag.png', 'data/gq_parrot.gif')
    elif len(sys.argv) == 5:
        parrot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 3:
        parrot(sys.argv[1], sys.argv[2])
    else:
        print("Please provide one source file and one destination file")
