""" Take a nominally b/w file and (hopefully) actually b/w it.
    The goal is to preserve alpha values but we'll see what happens.

    This will calculate the brightness of each pixel and then map those values
    to either black or white.
"""
from PIL import Image
import numpy as np

def binarize(image_path, out_path, threshold=178, duration=20):
    image = Image.open(image_path)

    frames = []
    for index in range(0, image.n_frames):
        image.seek(index)
        image2 = image.convert(mode='RGBA')
        im = np.array(image2)
        for i in range(im.shape[0]):
            for j in range(im.shape[1]):
                pixel = im[i,j]
                r, g, b, a = pixel
                mag = 0.2126 * r + 0.7152 * g + 0.0722 * b
                if mag > threshold:
                    im[i,j] = [255, 255, 255, a]
                else:
                    im[i,j] = [0, 0, 0, a]
        frames.append(Image.fromarray(im, mode='RGBA'))

    
    frames[0].save(out_path, save_all=True, append_images=frames[1:], optimize=False, loop=0, transparency=0, disposal=2, duration=duration)

if __name__ == '__main__':
    # this is complicated enough its almost ready to argparse
    if len(sys.argv) == 1:
        binarize('data/mega_blank_solid.gif', 'data/mega_solid.gif')
    elif len(sys.argv) == 5:
        binarize(sys.argv[1], sys.argv[2], threshold=sys.argv[3], duration=sys.argv[4])
    elif len(sys.argv) == 3:
        binarize(sys.argv[1], sys.argv[2])
    else:
        print("Please provide one source file and one destination file")

