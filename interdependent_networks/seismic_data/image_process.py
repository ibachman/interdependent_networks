from PIL import Image


def color_difference(color1, color2):
    r_1, g_1, b_1, c1 = color1
    r_2, g_2, b_2, c2 = color2

    diff = (max(r_1, r_2) - min(r_1, r_2)) + (max(g_1, g_2) - min(g_1, g_2)) + (max(b_1, b_2) - min(b_1, b_2))
    return diff


def brightness(color):
    r, g, b, c = color
    diff = ((r * 299) + (g * 587) + (b * 114))/1000
    return diff


def load_scale(img_name):
    no_color = (0,0,0,0)
    im = Image.open(img_name)  # Can be many different formats.
    pix = im.load()
    max_x, max_y = im.size
    scale_values = []
    x = max_x - 1
    for y in range(max_y):
        if pix[x,y] != no_color:
            scale_values.append(pix[x, y])
    return scale_values


def find_closest_color(color, colore_set):
    pure_white = (255,255,255,255)
    sky_blue = (118,199,228,255)
    blue = (110,142,183,255)
    ice_white = (248,250,245,255)
    black = (18,10,7,255)

    gray = (129,132,141,255)
    gray_2 = (205,208,211,255)
    gray_3 = (220, 227, 226, 255)

    discard_colors = [sky_blue, blue, ice_white,black, gray]
    min_diff = 500
    min_c = color
    for c in colore_set:
        diff = color_difference(c, color)
        if diff < min_diff:
            min_c = c
            min_diff = diff
    for c in discard_colors:
        diff = color_difference(c, color)
        if diff < min_diff:
            min_c = pure_white
            min_diff = diff

    return min_c


def create_values_matrix(img_name, scale_name, max_value, min_value):
    scale_values = load_scale(scale_name)
    values_matrix = []
    # create values list
    scale_len = len(scale_values)
    step = int((max_value - min_value)/scale_len)
    values = range(min_value, max_value, step)
    if len(values) > scale_len:
        values = values[0:scale_len]
    # turn list to dict
    dict_values = {}
    for i in range(scale_len):
        dict_values[scale_values[i]] = values[len(values)-(i+1)]

    white = (255, 255, 255, 255)
    im = Image.open(img_name)
    pix = im.load()
    max_x, max_y = im.size
    for y in range(max_y):
        values_matrix.append([])
        for x in range(max_x):
            if pix[x,y] != white:
                pix_value = dict_values[pix[x,y]]
                values_matrix[y].append(pix_value)
    # delete empty rows
    final_matrix = []
    for y in range(len(values_matrix)):
        if len(values_matrix[y]) > 0 :
            final_matrix.append(values_matrix[y])
    return final_matrix

def aux(name, save_name):
    scale = load_scale('map_scale2.png')
    white = (255, 255, 255, 255)
    im = Image.open(name) # Can be many different formats.
    pix = im.load()
    max_x, max_y = im.size
    print(im.size)  # Get the width and hight of the image for iterating over

    total = max_y * max_x
    i = 0
    for y in range(max_y):
        for x in range(max_x):
            if pix[x,y] != white:
                pix[x, y] = find_closest_color(pix[x, y], scale) # Set the RGBA Value of the image (tuple)
                i += 1
                percent = (i*100.0)/total
                print("{}%".format(percent), flush=True)



    im.save(save_name)  # Save the modified pixels as .png


#vs30_matrix = create_values_matrix("m_full_map.png", 'map_scale2.png', 2200, 0)

