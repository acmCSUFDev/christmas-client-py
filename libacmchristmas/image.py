# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from PIL import Image


# Assumes size is already correct
def prepare_image(img: Image.Image) -> np.array:
    return np.array(img.convert("RGBA")).ravel()


def resize_image(img: Image.Image, ix: int, iy: int) -> Image:
    return img.resize((ix, iy))


def load_direct(img: Image.Image, ix: int, iy: int) -> np.array:
    return prepare_image(resize_image(img, ix, iy))


def load_direct_from_disk(img: str, ix: int, iy: int) -> np.array:
    return load_direct(Image.open(img), ix, iy)
