#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math
import os
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col, oob):
    width = image["width"]
    height = image["height"]
    #Invalid method of indexing
    if 0 <= row < height and 0 <= col < width:
        return image["pixels"][row * width + col]
    if oob == "zero":
            return 0
    elif oob == "wrap":
        #Modulus can easily determine the new wrap distance
        nrow = row%height
        ncol = col%width
        return image["pixels"][nrow * image["width"] + ncol]
    elif oob == "extend":
        if row < 0:
            row = 0 #Assumes the row continues forth
        elif row >= height:
            row = height - 1 #Extends to the nearest row value
        
        if col < 0:
            col = 0
        elif col >= width:
            col = width - 1 #Extends to the nearest column value
        return image["pixels"][row * width + col]
    return 0


def set_pixel(image, row, col, color):
    image["pixels"][row * image["width"] + col] = color


def apply_per_pixel(image, func):
    result = {
        "height": image["height"],
        "width": image["width"],
        #Incorrect dict access
        "pixels": image["pixels"],
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255-color)


# HELPER FUNCTIONS

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

    Kernel will be represented as a dictionary of a 2d list of integers as it allows for relatively straight
    forward indexing and the size of the kernel.
    """
    if boundary_behavior in ["zero", "extend", "wrap"]:
        kersize = len(kernel["values"])
        rng = kersize// 2

        output = {
            "height": image["height"],
            "width": image["width"],
            "pixels": [0] * (image["height"] * image["width"])
        }
        
        for row in range(image["height"]):
            for col in range(image["width"]):
                total = 0
                for i in range(-rng ,rng + 1):
                    for j in range(-rng, rng + 1):
                        color = get_pixel(image, row+i, col+j, boundary_behavior)
                        kernel_val = kernel["values"][rng + i][rng + j]
                        total += kernel_val * color
                output["pixels"][row * image["width"] + col] = total
        return output

    else:
        return None
    


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
                pixel_index = row * image["width"] + col
                value = round(image["pixels"][pixel_index])
                if value < 0:
                    set_pixel(image, row, col, 0)
                elif value > 255:
                    set_pixel(image, row, col, 255)
                else:
                    set_pixel(image, row, col, value)
    return image

# FILTERS

def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    kernel = blur_kernel(kernel_size)
    new_image = correlate(image, kernel, "extend")
    return round_and_clip_image(new_image)
    

def blur_kernel(kernel_size):
    value = 1 / (kernel_size * kernel_size)
    kernel = {
        "size": kernel_size,
        "values": [[value for _ in range(kernel_size)] for _ in range(kernel_size)]}
    return kernel
def sharpen_kernel(kernel_size):
    value = 1 / (kernel_size * kernel_size)
    kernel = {
        "size": kernel_size,
        "values": [[-value for _ in range(kernel_size)] for _ in range(kernel_size)]}
    return kernel
def sharpened(image, kernel_size):

    sharp_kern = sharpen_kernel(kernel_size)

    cent = kernel_size // 2
    sharp_kern["values"][cent][cent] = 2 * image[] - (1/(kernel_size**2))

    new_image = correlate(image, sharp_kern, "extend")

    return new_image
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


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
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
    by the "mode" parameter.
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
    """
    kernel = {
        "size": 3,
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
    image = load_greyscale_image('test_images/python.png')
    #image = {"height": 3, "width": 2, "pixels": [20, 40, 60,  80, 100, 120],}
    new_image = sharpened(image,11)
    save_greyscale_image(new_image, 'pythonnew.png', mode = "PNG")
