#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing 2
"""

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import os
# import typing  # optional import
from PIL import Image

# COPY THE FUNCTIONS THAT YOU IMPLEMENTED IN IMAGE PROCESSING PART 1 BELOW!


# VARIOUS FILTERS


def get_width(image):
    return image["width"]

def get_height(image):
    return image["height"]

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color(image):
        #Utilizing the helper functions for a simpler code
        red, green, blue = split_image(image)

        red_filt = filt(red)
        green_filt = filt(green) 
        blue_filt = filt(blue)

        return combine_g_im(red_filt, green_filt, blue_filt)
    return color
def split_image(image):
    """
    Splits image into rgb parts
    """
    width = image["width"]
    height = image["height"]
    pixels = image["pixels"]

    red_px = []
    green_px = []
    blue_px = []

    #Loop through the tuples
    for pixel in pixels:
        red_px.append(pixel[0])
        green_px.append(pixel[1])
        blue_px.append(pixel[2])
    
    red = {"height": height, "width": width, "pixels": red_px}
    blue = {"height": height, "width": width, "pixels": blue_px}
    green = {"height": height, "width": width, "pixels": green_px}
    #Return in RGB order
    return red, green, blue
def combine_g_im(red, green, blue):
    """
    Combines red, green, and blue images into colored image
    """
    width = red["width"]
    height = red["height"]
    length = len(red["pixels"])
    r_px = red["pixels"]
    g_px = green["pixels"]
    b_px = blue["pixels"]

    combined_pixel = []

    #Combining each of the pixel values into the rgb tuple
    for i in range(length):
        combined_pixel.append((r_px[i], g_px[i], b_px[i]))

    #Return dictionary
    return {"height": height, "width": width, "pixels": combined_pixel}
#Previous Lab 1 Functions
def get_pixel(image, row, col, oob):
    """
    Returns a single integer pixel value according to the row and column
    considering the boundary behavior

    Args:
        image: dictionary containing information of the image with
        pixels, width, and height
        row: row of pixel
        col: column of pixel
        oob: boundary behavior ("extend", "zero", "wrap")

    Returns:
        Integer pixel value
    """
    width = image["width"]
    height = image["height"]
    # This is the normal case without considering
    # boundary behavior when the row or col is invalid
    if 0 <= row < height and 0 <= col < width:
        return image["pixels"][row * width + col]
    # For a zero behavior, return zero
    if oob == "zero":
        return 0
    # Wrap behavior
    elif oob == "wrap":
        # Modulus can easily determine the new wrap distance
        nrow = row % height
        ncol = col % width
        return image["pixels"][nrow * image["width"] + ncol]
    # Extend behavior which can be done simply with if and elif statements
    elif oob == "extend":
        # Rows
        if row < 0:
            row = 0  # Assumes the row continues
        elif row >= height:
            row = height - 1  # Extends to the nearest row value

        # Columns
        if col < 0:
            col = 0  # Assumes the column continues
        elif col >= width:
            col = width - 1  # Extends to the nearest column value
        return image["pixels"][row * width + col]
    return 0


def set_pixel(image, row, col, color):
    image["pixels"][row * image["width"] + col] = color


def apply_per_pixel(image, func):
    """
    Returns an image which applies a function to each pixel

    Args:
        image: dictionary containing information of the image with
        pixels, width, and height
        func: function

    Returns:
        Image
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        # Incorrect dict access
        "pixels": image["pixels"],
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col, "zero")
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result
def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for row in range(image["height"]):
        for col in range(image["width"]):
            # Want to use the fundamental method to find the
            # pixel_index without using the boundary condition
            pixel_index = row * image["width"] + col
            value = round(image["pixels"][pixel_index])
            if value < 0:
                set_pixel(image, row, col, 0)
            elif value > 255:
                set_pixel(image, row, col, 255)
            else:
                set_pixel(image, row, col, value)
    return image
def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE

    Kernel will be represented as a dictionary of a 2d list of
    integers as it allows for relatively straight
    forward indexing and the size of the kernel

    Ex.

    kernel = {
        "size": 11,
        "values": [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    }

    """
    if boundary_behavior in ["zero", "extend", "wrap"]:

        # Find kernel size
        kersize = kernel["size"]
        # Range of kernel which accounts that the indexing
        # will start from the center kernel
        rng = kersize // 2

        # Creating a new output image
        output = {
            "height": image["height"],
            "width": image["width"],
            "pixels": [0] * (image["height"] * image["width"]),
        }

        # Looping through the rows and columns
        for row in range(image["height"]):
            for col in range(image["width"]):
                # Equates to the total float value of using
                # the kernel on each individual pixel
                total = 0
                # Indexing allows for Kernel indexing to begin at center
                for i in range(-rng, rng + 1):
                    for j in range(-rng, rng + 1):
                        # Find pixel from original image which
                        # corresponds to where the kernel is being applied
                        color = get_pixel(image, row + i, col + j, boundary_behavior)
                        kernel_val = kernel["values"][rng + i][rng + j]
                        total += kernel_val * color
                set_pixel(output, row, col, total)
        return output
    # Edge case where boundary
    # condition is not provided or invalid
    else:
        return None
def inverted(image):
    # Code originally had 256-color which was incorrect
    inverted_img = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],
    }  
    return apply_per_pixel(inverted_img, lambda color: 255 - color)
def make_blur_filter(kernel_size):
    """
    Returns a blur filter similar to that of Lab 1
    """
    def bfilt(image):
        value = 1 / (kernel_size**2)
        kernel = {
            "size": kernel_size,
            # Constructs a 2D array with list comprehension
            "values": [[value for col in range(kernel_size)] 
                       for row in range(kernel_size)],
        }
        new_image = correlate(image, kernel, "extend")
        return round_and_clip_image(new_image)
    return bfilt
def make_sharpen_filter(kernel_size):
    """
    Returns sharpener filter similar to that of lab 1 for grey scale image
    """
    def sharp(image):
        value = 1 / (kernel_size * kernel_size)
        kernel = {
            "size": kernel_size,
            "values": [
                [-value for col in range(kernel_size)] for row in range(kernel_size)
            ],
        }

        # In the equation, we know that the center
        # pixel of the kernel will be 2 minus the kernel size
        cent = kernel_size // 2
        kernel["values"][cent][cent] += 2

        new_image = correlate(image, kernel, "extend")

        return round_and_clip_image(new_image)
    return sharp
def copy_image(image):
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:], 
    }
    return new_image
def edges(image):
    # Create the initial kernels for the edges
    # which we know can be utilized for all edge images
    """
    Returns an image with the edges defined according to an image

    Args:
        image: dictionary containing information of
        the image with pixels, width, and height

    Returns:
        Edge image
    """
    kernel_1 = {
        "size": 3,
        "values": [
            [
                -1,
                -2,
                -1,
            ],
            [0, 0, 0],
            [1, 2, 1],
        ],
    }
    kernel_2 = {
        "size": 3,
        "values": [
            [
                -1,
                0,
                1,
            ],
            [-2, 0, 2],
            [-1, 0, 1],
        ],
    }
    o_1 = correlate(image, kernel_1, "extend")
    o_2 = correlate(image, kernel_2, "extend")
    # Create the output image
    new_img = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"]),
    }

    for row in range(image["height"]):
        for col in range(image["width"]):
            opixel_1 = get_pixel(o_1, row, col, "extend")
            opixel_2 = get_pixel(o_2, row, col, "extend")

            # Performing the square root operation
            new_pixel = ((opixel_1**2) + (opixel_2**2)) ** (1 / 2)

            set_pixel(new_img, row, col, new_pixel)
    return round_and_clip_image(new_img)
def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    #Loop through for each filter in the list and apply it
    def filtr(image):
        image_copy = copy_image(image)
        for filt in filters:
            image_copy = filt(image_copy)
        return image_copy
    return filtr



# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    output_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    #_ is a useless variable, this is just to loop through the columns
    for _ in range(ncols):
        #Process of seam carving
        new_image = greyscale_image_from_color_image(output_image)
        nrg_img = compute_energy(new_image)
        cem = cumulative_energy_map(nrg_img)
        seam = minimum_energy_seam(cem)
        output_image = image_without_seam(output_image, seam)
    return output_image



# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    output = {
        "height": image["height"],
        "width": image["width"],
        "pixels": []
    }
    for var in image["pixels"]:
        #Formula provided by the 6.101 page
        new = round(.299 * var[0] + .587 * var[1] + .114 * var[2])
        output["pixels"].append(new)
    return output
def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function) greyscale image, computes a "cumulative energy map" as described
    in the lab 2 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    width = energy['width']
    height = energy['height']
    pixels = energy['pixels'][:]

    for row in range(1, height):
        for col in range(width):
            #How to find the index
            i = row*width+col
            #Useful var to store
            var = row - 1

            adj_nrg = []
            #Pixel Above
            adj_nrg.append(pixels[(var) * width + col])

            #Pixel to left
            if col > 0:
                adj_nrg.append(pixels[(var) * width + (col-1)])
            #Pixel on the edge cases of the array
            if col < width - 1:
                adj_nrg.append(pixels[(var) * width + (col+1)])

            #Takes the minimum of the adjacent energies for the column path
            min_adj_nrg = min(adj_nrg)

            pixels[i] += min_adj_nrg
    output = {
        "height": energy["height"],
        "width": energy["width"],
        "pixels": pixels
    } 
    return output

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map dictionary, returns a list of the indices into
    the 'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    width = cem["width"]
    height = cem["height"]
    pixels = cem["pixels"]

    seam = []

    #Starts below top row
    r_start = height - 1
    i_start = [r_start * width + col for col in range(width)]
    #Bottom row
    btm_row = [pixels[i] for i in i_start]

    #Finding the minimum column
    min_col = btm_row.index(min(btm_row))
    min_i = r_start * width + min_col

    seam.append(min_i)

    curr = min_col

    #This specific loop will loop backwards in -1 steps
    for row in range(r_start - 1, -1, -1):

        #Possible candidates for the minimum seam
        poss = []
        #Edge cases
        if curr > 0:
            i_lef = row * width + (curr - 1)
            nrg_lef = pixels[i_lef]
            poss.append((nrg_lef, curr-1, i_lef))

        #Middle cases
        i_mid = row * width + curr
        nrg_mid = pixels[i_mid]
        poss.append((nrg_mid, curr, i_mid))

        #Edge cases
        if curr < width - 1:
            i_rgt = row * width + (curr +1)
            nrg_rgt = pixels[i_rgt]
            poss.append((nrg_rgt, curr+1, i_rgt))

        #Defining the minimum potential

        #Didn't actually need the key because of the way min works
        min_pot = min(poss, key = lambda x: (x[0], x[1]))

        #Updating the variables
        curr = min_pot[1]
        seam.append(min_pot[2])
    seam.reverse()
    return seam

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    width = image['width']
    height = image['height']
    pixels = image['pixels']


    #New pixels
    new = []
    #Loops through while considering the deletion column to not add.
    for row in range(height):
        seam_i = seam[row]
        #Take modulus to find the floored column
        del_col = seam_i % width
        for col in range(width):
            if col != del_col:
                i = row * width + col
                new.append(pixels[i])
    new_image = {
        'height': height,
        'width': width - 1,
        'pixels': new
    }
    return new_image

def custom_feature(image, exposure_factor):
    """
    Adjusts the exposure of the given image by scaling pixel with the exposure factor.

    Parameters:
        image: The original image to adjust.
        exposure_factor: The factor by which to adjust exposure. 
        >1 should increases brightness, while <1 decreases brightness.

    Returns:
        output: Image with the new exposure
    """
    output = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:]
    }
    #This clips the values such that it is a normal 6.101 valid image
    def flooring(value):
        return max(0, min(255, int(round(value))))
    
    #Loops through and applies the exposure filter
    for i in range(len(output["pixels"])):
        red, green, blue = output["pixels"][i]

        n_red = flooring(red * exposure_factor)
        n_green = flooring(green * exposure_factor)
        n_blue = flooring(blue * exposure_factor)

        output["pixels"][i] = (n_red,n_green,n_blue)
    return output
# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES

def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for (col, val) in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"]-1:
            out += "\n "
    print(out)


def print_color_values(image):
    """
    Given a color image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that RGB values will be rounded to the nearest int.
    """
    out = f"Color image with {image['height']} rows"
    out += f" and {image['width']} columns:\n"
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        for color in range(3):
            val = str(round(pixel[color]))
            space_vals.append((col, color, val))
            space_sizes[(col, color)] = max(len(val), space_sizes.get((col, color), 0))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for (col, color, val) in space_vals:
        space_val = val.center(space_sizes[(col, color)])
        if color == 0:
            out += f" ({space_val}"
        elif color == 1:
            out += f" {space_val} "
        else:
            out += f"{space_val})"
        if col == image["width"]-1 and color == 2:
            out += "\n"
    print(out)


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)
    # save image in folder specified (by default the current folder)
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()



if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    #pass
    #color_inverted = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    #filter1 = color_filter_from_greyscale_filter(edges)
    #filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    #filt = filter_cascade([filter1, filter1, filter2, filter1])
    img = load_color_image('../r3/flood_input.png')
    print(get_height(img))
    print(get_width(img))
