#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!

def in_bound(dim , s):
    """Get inbound pixel coordinate for out-of-bound

    Args:
        dim (int): Image height or width
        s (int): Coordinate 

    Returns:
        int: Inbound
    """
    if s <= -1:
        return 0
    elif s >= dim:
        return dim - 1
    else:
        return s

def get_pixel(image, x, y):
    """Get pixel of image from coordinates

    Args:
        image (dict): Image to get pixel from
        x (int): x coordinate
        y (int): y coordinate

    Returns:
        int: Pixel value
    """
    x = in_bound(image["height"], x)
    y = in_bound(image["width"], y)
    
    return image['pixels'][ x * image["width"] + y]


def set_pixel(image, c):
    image['pixels'].append(c)


def apply_per_pixel(image, func):
    """Apply func on every pixel of image

    Args:
        image (dict) : Image to be applied func at
        func (function): Function to be applied

    Returns:
        dict: Modified image
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, newcolor)
    return result


def inverted(image):
    """Invert given image

    Args:
        image (dict): Input image

    Returns:
        dict: Inverted image
    """
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    kernel = [k1, k2, k3, ... kn]
    """
    result = {"height":image["height"],
    "width":image["width"],
    "pixels": []}

    kernel_size = int(len(kernel) ** (1/2))
    num_layers = int((kernel_size - 1)/2)  # Layers of kernel excluding center
    for x in range(image["height"]):
        for y in range(image["width"]):
            newpixel = 0.0
            for h in range(kernel_size):
                for w in range(kernel_size):
                    # O[x,y] = (K[h,w] * I[x - num_layers + h, y - num_layers + w])
                    newpixel += kernel[h * kernel_size + w] * get_pixel(image,x - num_layers + h, y - num_layers + w)
            set_pixel(result, newpixel)
    return result
                                
                
            

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    
    for idx, pixel in enumerate(image["pixels"]):
        if round(pixel) < 0 :
            image["pixels"][idx] = 0
        elif round(pixel) > 255 :
            image["pixels"][idx] = 255
        else:
            image["pixels"][idx] = round(pixel)
    return image



# FILTERS

# helpers
def get_blur_kernel(n):
    """ Get kernel to blur an image

    Args:
        n (int): kernel size

    Returns:
        list: kernel
    """
    return [1/n**2] * n**2

def blurred(image, n ,correct = True):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = get_blur_kernel(n)
    # then compute the correlation of the input image with that kernel
    correlated = correlate(image, kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    if correct:
        return round_and_clip_image(correlated)
    else:
        return correlated

def sharpened(image, n):
    """Sharpen the given image

    Args:
        image (dict): Given image
        n (int): Kernel size

    Returns:
        dict: Sharpened image
    """
    result = {"height": image["height"],
    "width":image["width"],
    "pixels":[]}

    result["pixels"] = [2*x - y for x,y in zip(image["pixels"], blurred(image, n ,False)["pixels"])]

    return round_and_clip_image(result)

def edges(i):
    """Performs Sobel Operation on given image

    Args:
        i (dict): Input image
    Returns:
        dict: Resulting Image
    """
    Oxy = i.copy()
    Kx = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    Ky = [-1, -2, -1, 0, 0, 0, 1, 2, 1]

    Ox = correlate(i, Kx)
    Oy = correlate(i,Ky)

    Oxy["pixels"] = [ (x**2 + y**2)**(1/2) for x, y in zip(Ox["pixels"], Oy["pixels"])]

    result = round_and_clip_image(Oxy)
    return result


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    # 3.3 - Run your inversion filter
    # bluegill = load_image("test_images/bluegill.png")
    # inverted_bluegill = inverted(bluegill)
    # save_image(inverted_bluegill, "test_images/inverted_bluegill.png")
    pass


    
