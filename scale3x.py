""" Implements Scale3x/AdvMAME3x scaling algorithm as described in the below link.
    https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms#Scale3%C3%97/AdvMAME3%C3%97_and_ScaleFX
    Why did I choose this one? looked easy
"""
import sys
from PIL import Image, ImageFilter
import numpy as np
from copy import deepcopy
import datetime
import pprint
pp = pprint.PrettyPrinter(indent=4)

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
    new_shape = [0, 0, 4]
    new_shape[0] = shape[0]*3
    new_shape[1] = shape[1]*3
    shape = tuple(new_shape)
    out_image = np.zeros(new_shape, dtype=np.uint8)
    for i in range(orig.shape[0]):
        for j in range(orig.shape[1]):
            # okay i dont know the best way to make this simpler but w/e
            x = 3*i; y = 3*j
            for a in range(3):
                for b in range(3):
                    out_image[x+a][y+b] = orig[i,j]

            pa, pb, pc, pd, pe, pf, pg, ph, pi = getpix(orig, i, j)

            # common pairings
            bd = np.all(pb==pd); dh = np.all(pd==ph); bf = np.all(pb==pf); ce = np.all(pc==pe)
            fh = np.all(pf==ph); ae = np.all(pa==pe); eg = np.all(pe==pg); ei = np.all(pe==pi)
            if bd and not dh and not bf:
                out_image[x, y] = pd
            if (bd and not dh and not bf and not ce) \
                    or (bf and not bd and not fh and not ae):
                out_image[x+1, y] = pb
            if bf and not bd and not fh:
                out_image[x+2, y] = pf
            if (dh and not fh and not bd and not ae) \
                    or (bd and not dh and not bf and not eg):
                out_image[x, y+1] = pd
                out_image[x+1, y+1] = pe
            if (bf and not bd and not fh and not ei) \
                    or (fh and not bf and not dh and not ce):
                out_image[x+2, y+1] = pf
            if dh and not fh and not bd:
                out_image[x, y+2] = pd
            if (fh and not bf and not dh and not eg) \
                    or (dh and not fh and not bd and not ei):
                out_image[x+1, y+2] = ph
            if fh and not bf and not dh:
                out_image[x+2, y+2] = pf

    out_image = Image.fromarray(out_image, mode='RGBA')
    if out_path:
        out_image.save(out_path)

    return out_image

def getpix(orig, i, j):
    shape = orig.shape
    if i == 0:
        # left border
        i_vals = [i, i, i+1]
    elif i >= shape[0] - 1:
        # right border
        i_vals = [i-1, i, i]
    else:
        # center
        i_vals = [i-1, i, i+1]
    if j >= shape[1] - 1:
        # lower border
        j_vals = [j-1, j, j]
    elif j == 0:
        # upper border
        j_vals = [j, j, j+1]
    else:
        # center
        j_vals = [j-1, j, j+1]

    pa = orig[i_vals[0], j_vals[0]]; pb = orig[i_vals[1], j_vals[0]]; pc = orig[i_vals[2], j_vals[0]]
    pd = orig[i_vals[0], j_vals[1]]; pe = orig[i_vals[1], j_vals[1]]; pf = orig[i_vals[2], j_vals[1]]
    pg = orig[i_vals[0], j_vals[2]]; ph = orig[i_vals[1], j_vals[2]]; pi = orig[i_vals[2], j_vals[2]]
    return pa, pb, pc, pd, pe, pf, pg, ph, pi

def color_correct(image):
    """ Sorts images into large contiguously-colored areas and then squashes the colors down
        In theory.
    """
    out_image = deepcopy(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j,3] == 0:
                continue
            # for neighbor in (+) neighbors, calculate color distance
            neighbors = []
            if i > 0:
                neighbors.append(image[i-1, j])
            if i < image.shape[0]-1:
                neighbors.append(image[i+1, j])
            if j > 0:
                neighbors.append(image[i, j-1])
            if j < image.shape[1]-1:
                neighbors.append(image[i, j+1])
            distances = np.zeros(len(neighbors))
            index = 0
            mindex = 0
            for neighbor in neighbors:
                r2 = (int(image[i,j,0]) - int(neighbor[0]))**2
                g2 = (int(image[i,j,1]) - int(neighbor[1]))**2
                b2 = (int(image[i,j,2]) - int(neighbor[2]))**2
                a2 = (int(image[i,j,3]) - int(neighbor[3]))**2
                distances[index] = r2+g2+b2+a2
                if distances[mindex] > distances[index] or distances[mindex] == 0:
                    mindex = index
                index += 1
            # take closest neighbor
            out_image[i,j] = neighbors[mindex]
            if np.all(out_image[i,j] != image[i,j]):
                print(out_image[i,j], image[i,j], i, j)
    return out_image

def simplify_colors(in_image):
    """ pull colors into their "most common" neighbor

        figure out which colors are most common, then create map of every color
        to the closest "most common" neighbor to its original color. Then
        squash.

    """
    colors = in_image.getcolors(10000)
    colormap = {}
    rare_colors = []
    common_colors = []
    threshold = 0.01*in_image.width*in_image.height
    for color in colors:
        c = np.array(color[1])
        black = np.all(c[0:3] < 10)
        white = np.all(c > 250)
        if black:
            colormap[color[1]] = (0, 0, 0, 255)
        elif white:
            colormap[color[1]] = (255, 255, 255, 255)
        elif color[0] > threshold:
            colormap[color[1]] = color[1] # map to itself
            common_colors.append(color[1])
        else:
            rare_colors.append(color[1])

    # squash the colorspace
    for color in rare_colors:
        if color[3] < 255: # if not completely opaque, make 100% transparent
            colormap[color] = (255, 255, 255, 0)
            continue
        # find nearest neighbor to map to
        if not color in colormap:
            colormap[color] = get_closest(color, common_colors)
    
    image = np.array(in_image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            image[i,j] = colormap[tuple(image[i,j])]

    
    im = Image.fromarray(image, mode='RGBA')
    colors = im.getcolors(len(colormap.keys())) # get every POSSIBLE color left in the image
    labeled_image = label(image, colors)
    '''
    original = deepcopy(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # get subsection
            i_min = max(0, i-1); i_max = min(image.shape[0]+1, i+2)
            j_min = max(0, j-1); j_max = min(image.shape[1]+1, j+2)
            circle = original[i_min:i_max, j_min:j_max]
            #print(list(range(i_min, i_max)), list(range(j_min, j_max)))
            new_color, count = get_unique(circle)
            circle = image[i_min:i_max, j_min:j_max]
            other_new_color, other_count = get_unique(circle)
            if np.all(new_color == other_new_color):
                image[i,j] = new_color
            elif other_count > count:
                image[i, j] = other_new_color
            else:
                image[i, j] = new_color
    '''
    return im

def label(image, colors):
    labelled_image = np.zeros(image.shape[0:2])
    BKGND = 0
    labels = [BKGND]
    max_label = 0
    equivalences = {}
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j, 3] == 0 or tuple(image[i, j]) == (0, 0, 0, 255):
                # set to background if transparent or black
                labelled_image[i,j] = BKGND
            else:
                # take the same value as your west/north neighbors IF they arent BKGND
                # uses the assumption that every new color is surrounded by black
                if i > 0:
                    west = labelled_image[i-1, j]
                else:
                    west = BKGND
                if j > 0:
                    north = labelled_image[i, j-1]
                else:
                    north = BKGND
                if west == BKGND and north == BKGND:
                    max_label += 1
                    labelled_image[i, j] = max_label
                    labels.append(max_label)
                elif west == BKGND:
                    labelled_image[i, j] = north
                elif north == BKGND:
                    labelled_image[i, j] = west
                elif west == north:
                    labelled_image[i, j] = west
                else: # combine the two regions
                    labelled_image[i, j] = min(west, north)
                    equivalences[max(west,north)] = min(west, north)

    colors = {}
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # update which section of the image this pixel is part of
            label = labelled_image[i, j]
            if label in equivalences:
                labelled_image[i, j] = equivalences[label]

            # collect statistics on this section of the image
            label = labelled_image[i, j]
            cur_pix = tuple(image[i,j])
            if label in colors:
                if cur_pix in colors[label]:
                    colors[label][cur_pix] += 1
                else:
                    colors[label][cur_pix] = 1
            else:
                colors[label] = {}
                colors[label][cur_pix] = 1

    # one last iteration through the image to adjust the colors again
    faster_colors = {} # fill this up so we dont continually have to find the max value
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if labelled_image[i, j] == BKGND:
                continue
            if labelled_image[i,j] in faster_colors:
                image[i,j] = faster_colors[labelled_image[i,j]]
                continue
            countmap = colors[labelled_image[i,j]]
            mvp = None
            count = 0
            for color in countmap: # colors associated with this label
                if countmap[color] > count:
                    mvp = color
                    count = countmap[color]
            image[i,j] = mvp
    

    return image




def get_unique(circle):
    unique_values = {}
    max_val = 0
    max_color = 0
    for i in range(circle.shape[0]):
        for j in range(circle.shape[1]):
            key = tuple(circle[i,j])
            if key in unique_values:
                unique_values[key] += 1
            else:
                unique_values[key] = 1
            if unique_values[key] > max_val:
                max_val = unique_values[key]
                max_color = circle[i,j]
    return max_color, max_val
    


def get_closest(color, color_list):
    minimum = (-1, -1, -1, -1)
    mindist = 196000 # larger than the largest possible number
    for c_color in color_list:
        # calculate distance
        dist = color_dist(color, c_color)
        if dist < mindist and not (color[3] == 255 and c_color[3] != 255):
            minimum = c_color
            mindist = dist
    if color[3] == 255 and minimum[3] != 255:
        print(color, minimum, color_list)
    return minimum



def color_dist(color1, color2):
    dr = (color1[0] - color2[0])**2
    dg = (color1[1] - color2[1])**2
    db = (color1[2] - color2[2])**2
    return (dr+dg+db)**0.5



if __name__ == '__main__':
    im = Image.open('parrot.gif')
    #im = Image.open('test_image.png')
    frames = []
    #for index in range(1):
    for index in range(im.n_frames):
        im.seek(index)
        origname = 'orig_frame_' + str(index)
        #newname = 'new_frame_' + str(index)
        frame = deepcopy(im.convert(mode='RGBA'))
        sharp = frame.filter(ImageFilter.SHARPEN)
        orig_frame = simplify_colors(scale3x(in_image=sharp))
        orig_frame.save(origname+'.png')
        frames.append(orig_frame)
        #new_frame = Image.fromarray(color_correct(np.array(deepcopy(orig_frame))), mode='RGBA')
        #new_frame.save(newname+'.png')
        pp.pprint(orig_frame.getcolors())

    pp.pprint(frames[0].__dict__)
    pp.pprint(frames[0].getcolors())
    frames[0].save('3xbigger_parrot.gif', save_all=True, append_images=frames[1:], optimization=False, duration=50, loop=0, disposal=2, transparency=0)
    frames[0].save('solid_3xbigger_parrot.gif', save_all=True, append_images=frames[1:], optimization=False, duration=50, loop=0, disposal=2)
