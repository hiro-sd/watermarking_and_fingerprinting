import numpy as np
import pytest

from attacks import (
    brightness,
    center_crop,
    gaussian_noise,
    jpeg_compression,
    resize,
    rotate,
)

from helpers import textured_rgb_image


@pytest.mark.parametrize(
    "attack",
    [
        lambda image: jpeg_compression(image, quality=70),
        lambda image: resize(image, scale=0.5),
        lambda image: center_crop(image, crop_ratio=0.1),
        lambda image: rotate(image, angle=5),
        lambda image: gaussian_noise(image, sigma=8, seed=42),
        lambda image: brightness(image, factor=1.2),
    ],
)
def test_attacks_preserve_size_and_rgb_mode(attack):
    image = textured_rgb_image(96)
    attacked = attack(image)
    assert attacked.size == image.size
    assert attacked.mode == "RGB"


def test_gaussian_noise_is_reproducible_with_seed():
    image = textured_rgb_image(64)
    first = gaussian_noise(image, sigma=10, seed=7)
    second = gaussian_noise(image, sigma=10, seed=7)
    np.testing.assert_array_equal(np.asarray(first), np.asarray(second))


@pytest.mark.parametrize(
    ("operation", "message"),
    [
        (lambda image: jpeg_compression(image, quality=0), "quality"),
        (lambda image: resize(image, scale=0), "scale"),
        (lambda image: center_crop(image, crop_ratio=0.5), "crop_ratio"),
        (lambda image: gaussian_noise(image, sigma=-1), "sigma"),
        (lambda image: brightness(image, factor=-1), "factor"),
    ],
)
def test_invalid_attack_parameters_are_rejected(operation, message):
    with pytest.raises(ValueError, match=message):
        operation(textured_rgb_image(32))
