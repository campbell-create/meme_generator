import sys
from PIL import Image, ImageChops
from copy import deepcopy
import numpy as np


COLORS = [
    (255, 141, 139),
    (254, 214,137),
    (136, 255, 137),
    (135, 255, 255),
    (139, 181, 254),
    (215, 140, 255),
    (255, 140, 255),
    (255, 104, 247),
    (254, 108, 183),
    (255, 105, 104),
]


def color_dist(color1, color2):
    squ_diffs = [(c1-c2)**2 for c1,c2 in zip(color1, color2)]
    return sum(squ_diffs)**0.5


def color_by_pixel(image, color):
    width = image.shape[0]
    height = image.shape[1]
    for x in range(width):
        for y in range(height):
            if image[x,y,3] < 155:
                image[x,y] = [0, 0, 0, 0]
                continue
            if color_dist(image[x, y][0:3], [0, 0, 0]) < 50:
                image[x][y] = [color[0], color[1], color[2], 255]
    return Image.fromarray(image, mode='RGBA').convert('RGB')


def multiply(image1, image2):
    width = image1.shape[0]
    height = image1.shape[1]
    array = np.zeros(list(image1.shape), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            c1 = image1[x,y]
            c2 = image2[x,y]
            cout = [np.uint8(int(p1)*int(p2)/255) for p1,p2 in zip(c1, c2)]
            array[x,y] = cout
    return Image.fromarray(array, mode='RGBA')


def party(file_path, out_file_path, replace_black=False, num_frames=10, offset=0):
    ''' Takes an image and makes it party.

        just because this produces gifs doesnt mean that it will
        produce gifs *for mattermost*
        you probably will need to resize the image
    '''
    print(file_path, out_file_path, replace_black, num_frames, offset)
    im = Image.open(file_path).convert('RGBA')
    out_images = []
    for index in range(0, num_frames):
        i = (index + offset) % len(COLORS)
        print(i)
        if not replace_black:
            color_image = Image.new('RGBA', (im.height, im.width), COLORS[i])
            image = multiply(np.array(color_image), np.array(im))
            out_images.append(image.convert('RGB'))
        else:
            image = color_by_pixel(np.array(deepcopy(im)), COLORS[i])
            out_images.append(image)

    for i in range(len(out_images)):
        out_images[i].save("frame" + str(i) + ".png")
    out_images[0].save(out_file_path, save_all=True, append_images=out_images[1:], optimize=False, duration=50, loop=0, transparency=0, disposal=2)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        party('smile_cry.png', 'smile_cry.gif')
    elif len(sys.argv) == 6:
        if sys.argv[3] == "True":
            replace_black = True
        else:
            replace_black = False
        party(sys.argv[1], sys.argv[2], replace_black=replace_black, num_frames=int(sys.argv[4]), offset=int(sys.argv[5]))
    elif len(sys.argv) == 4:
        if sys.argv[3] == "True":
            replace_black = True
        else:
            replace_black = False
        party(sys.argv[1], sys.argv[2], replace_black=replace_black)
    elif len(sys.argv) != 3:
        print("Please provide one source file and one destination file")
    else:
        party(sys.argv[1], sys.argv[2])

