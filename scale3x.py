""" Implements Scale3x/AdvMAME3x scaling algorithm as described in the below link.
    https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms#Scale3%C3%97/AdvMAME3%C3%97_and_ScaleFX
    Why did I choose this one? looked easy
"""
import sys
from PIL import Image, ImageFilter
import numpy as np
from copy import deepcopy
import datetime
import csv
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

def simplify_colors(in_image, in_colors=None):
    """ pull colors into their "most common" neighbor

        figure out which colors are most common, then create map of every color
        to the closest "most common" neighbor to its original color. Then
        squash.

    """
    colors = in_image.getcolors((in_image.width * in_image.height) * 2)
    colormap = {}
    rare_colors = []
    common_colors = []
    threshold = 0.01*in_image.width*in_image.height
    if in_colors:
        common_colors = in_colors
    for color in colors:
        c = np.array(color[1])
        black = np.all(c[0:3] < 20)
        white = np.all(c > 250)
        if black:
            colormap[color[1]] = (0, 0, 0, 255)
        elif white:
            colormap[color[1]] = (255, 255, 255, 255)
        elif ((not in_colors) and color[0] > threshold):
            colormap[color[1]] = color[1] # map to itself
            common_colors.append(color[1])
        elif in_colors and color[1] in in_colors:
            colormap[color[1]] = color[1] # map to itself
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
    im.save('colorsquash.png')
    colors = im.getcolors(len(colormap.keys())) # get every POSSIBLE color left in the image
    labeled_image = label(image, colors)
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
                elif np.all(image[i - 1, j] == image[i, j - 1]):
                    # different labels, neither are background.
                    # combine the two regions IF THE COLORS ARE THE SAME

                    # every time i implement this i forget about this case:
                    # the min of west & north might not be the actual "correct" label
                    # here because it's possible that min(west,north) is the max of
                    # another equivalence pair
                    keep = min(west, north)
                    toss = max(west, north)
                    labelled_image[i, j] = keep
                    while keep in equivalences:
                        keep = equivalences[keep]
                    equivalences[toss] = keep
                else:
                    # diff labels, neither R BKGND, both colors diff.
                    # Get closest color value to the current pixel
                    # we dont have to worry about west/north being BKGND because
                    # we just checked theyre not
                    closest = get_closest(image[i,j], [image[i - 1, j], image[i, j - 1]])
                    if np.all(image[i-1, j] == closest):
                        labelled_image[i, j] = west
                    else:
                        labelled_image[i, j] = north

    colors = {}
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # update which section of the image this pixel is part of
            label = labelled_image[i, j]
            while label in equivalences:
                label = equivalences[label]
            
            labelled_image[i, j] = label

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
    return minimum



def color_dist(color1, color2):
    try:
        dr = (float(color1[0]) - float(color2[0]))**2
        dg = (float(color1[1]) - float(color2[1]))**2
        db = (float(color1[2]) - float(color2[2]))**2
        return (int(dr+dg+db))**0.5
    except:
        print("EXCEPTION:", color1, color2)
        raise


def process_input(args):
    im = Image.open(args[1])
    if args[1][-4:] == '.gif':
        is_gif = True
    else:
        is_gif = False
    output_path = args[2]
    colors = None
    if len(args) >= 4:
        cleanup = args[3] == 'Y'
        print(args[3])
    if len(args) >= 5:
        colors = []
        with open(args[4]) as in_colors:
            reader = csv.reader(in_colors, delimiter=',')
            for row in reader:
                color = []
                for item in row:
                    color.append(int(item))
                if color:
                    colors.append(tuple(color))
        print(colors)
    return im, output_path, is_gif, cleanup, colors

def median_filter(im):
    image = np.array(im)
    orig = deepcopy(image)

    for i in range(orig.shape[0]):
        for j in range(orig.shape[1]):
            x1 = max(0, i-1); x2 = min(i+2, orig.shape[0])
            y1 = max(0, j-1); y2 = min(j+2, orig.shape[1])
            mtx = deepcopy(image[x1:x2, y1:y2])
            # reshape
            out_mtx = np.zeros(mtx.shape[0]*mtx.shape[1], dtype=tuple)
            for a in range(mtx.shape[0]):
                for b in range(mtx.shape[1]):
                    out_mtx[a*mtx.shape[1]+b] = tuple(mtx[a,b])
            out_mtx.sort()
            image[i,j] = out_mtx[len(out_mtx) // 2]
    return Image.fromarray(image)



if __name__ == '__main__':
    im, output_path, is_gif, cleanup_only, in_colors = process_input(sys.argv)
    if is_gif:
        n_frames = im.n_frames
    else:
        n_frames = 1
    frames = []
    for index in range(n_frames):
        im.seek(index)
        origname = 'orig_frame_' + str(index)
        frame = deepcopy(im.convert(mode='RGBA'))
        if cleanup_only:
            orig_frame = simplify_colors(in_image=frame, in_colors=in_colors)
            orig_frame.save('pre_median.png')
            orig_frame = median_filter(orig_frame)
        else:
            sharp = frame.filter(ImageFilter.SHARPEN)
            orig_frame = simplify_colors(scale3x(in_image=sharp))
        orig_frame.save(origname+'.png')
        frames.append(orig_frame)
        pp.pprint(orig_frame.getcolors())

    pp.pprint(frames[0].__dict__)
    pp.pprint(frames[0].getcolors())
    if is_gif:
        frames[0].save(output_path, save_all=True, append_images=frames[1:], optimization=False, duration=50, loop=0, disposal=2, transparency=0)
        frames[0].save('solid_' + output_path, save_all=True, append_images=frames[1:], optimization=False, duration=50, loop=0, disposal=2)
    else:
        frames[0].save(output_path)
