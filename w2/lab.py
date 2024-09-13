#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import os
from PIL import Image


# NO ADDITIONAL IMPORTS ALLOWED!
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


def inverted(image):
    # Code originally had 256-color which was incorrect
    inverted_img = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"][:],
    }
    return apply_per_pixel(inverted_img, lambda color: 255 - color)


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


# FILTERS
def blurred(image, kernel_size):
    """
    Returns a blurred image according to a kernel size

    Args:
        image: dictionary containing information of the image
        with pixels, width, and height
        kernel_size: allows for blur_kernel to take input and find the blur kernel

    Returns:
        Blurred image
    """
    # Defined helper function
    kernel = blur_kernel(kernel_size)
    new_image = correlate(image, kernel, "extend")
    return round_and_clip_image(new_image)


def blur_kernel(kernel_size):
    """
    Returns a blurred kernel according to a kernel size

    Args:
        kernel_size: controls the size and values of the kernel

    Returns:
        Blurred kernel
    """
    # Take the float value corresponding to the
    # kernel size as this would add to 1
    value = 1 / (kernel_size**2)
    kernel = {
        "size": kernel_size,
        # Constructs a 2D array with list comprehension
        "values": [[value for col in range(kernel_size)] for row in range(kernel_size)],
    }
    return kernel


def sharpen_kernel(kernel_size):
    """
    Returns a sharpened kernel according to a kernel size

    Args:
        kernel_size: controls the size and values of the kernel

    Returns:
        Sharp kernel
    """

    # Extremely similar to blurred
    # but is simply the negative values
    value = 1 / (kernel_size * kernel_size)
    kernel = {
        "size": kernel_size,
        "values": [
            [-value for col in range(kernel_size)] for row in range(kernel_size)
        ],
    }
    return kernel


def sharpened(image, kernel_size):
    """
    Utilizing the correlate with a kernel method instead of explicit.

    Returns a sharpened image according to an image and kernel size

    Args:
        image: dictionary containing information of the image
        with pixels, width, and height
        kernel_size: controls the size and values of the kernel

    Returns:
        Sharpened image
    """
    # Create the blurred image for S_r,c = 2 I_r,c - B_r,c
    sharp_kern = sharpen_kernel(kernel_size)

    # In the equation, we know that the center
    # pixel of the kernel will be 2 minus the kernel size
    cent = kernel_size // 2
    sharp_kern["values"][cent][cent] = 2 - (1 / (kernel_size**2))

    new_image = correlate(image, sharp_kern, "extend")

    return round_and_clip_image(new_image)


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

    for col, val in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"] - 1:
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
    # image = load_greyscale_image('test_images/construct.png')
    # image = {"height": 3, "width": 2, "pixels": [20, 40, 60,  80, 100, 120],}
    # new_image = blurred(image, 11)
    # save_greyscale_image(new_image, 'newconstruct.png', mode = "PNG")
    print("Finished")
