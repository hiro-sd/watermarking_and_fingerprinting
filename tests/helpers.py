import numpy as np
from PIL import Image


def textured_rgb_image(size: int = 256) -> Image.Image:
    y, x = np.indices((size, size))
    red = 110 + 45 * np.sin(x / 9) + 25 * np.cos(y / 13)
    green = 100 + 40 * np.cos(x / 15) + 35 * ((x // 24 + y // 24) % 2)
    blue = 105 + 50 * np.sin((x + y) / 17)
    pixels = np.stack((red, green, blue), axis=-1)
    return Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), mode="RGB")
