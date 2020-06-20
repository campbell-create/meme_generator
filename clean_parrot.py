

""" This should take in one party parrot and create two distinct gifs:
    one is regular transparency, without haloing and whatnot
    the other is no transparency, white background, no haloing & whatnot

    right now it just makes the transparent background white 
"""


def set_background(in_path, out_path):
    im = Image.open(in_path)
    frames = []

    for index in range(0, in.n_frames):
        im.seek(index)
        im2 = im.convert(mode='RGBA')
        frame = np.array(im2)
        original = deepcopy(frame)
        for i in range(frame.shape[0]):
            for j in range(frame.shape[1]):
                
