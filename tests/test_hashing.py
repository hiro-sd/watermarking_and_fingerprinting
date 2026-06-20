import numpy as np
import pytest
from PIL import Image, ImageEnhance

from fingerprint import dhash, hamming_distance, hash_to_hex, phash


def gradient_image(horizontal: bool = True, size: int = 128) -> Image.Image:
    line = np.linspace(0, 255, size, dtype=np.uint8)
    pixels = np.tile(line, (size, 1))
    if not horizontal:
        pixels = pixels.T
    return Image.fromarray(pixels, mode="L")


def textured_image(size: int = 128) -> Image.Image:
    """Create a deterministic image with several spatial frequencies."""
    y, x = np.indices((size, size))
    pixels = (
        80
        + 40 * np.sin(x / 7)
        + 35 * np.cos(y / 11)
        + 25 * ((x // 16 + y // 16) % 2)
    )
    return Image.fromarray(np.clip(pixels, 0, 200).astype(np.uint8), mode="L")


@pytest.mark.parametrize("algorithm", [dhash, phash])
def test_identical_images_have_zero_distance(algorithm):
    image = gradient_image()
    assert hamming_distance(algorithm(image), algorithm(image.copy())) == 0


def test_dhash_detects_opposite_gradients():
    increasing = gradient_image()
    decreasing = Image.fromarray(np.fliplr(np.asarray(increasing)))
    assert hamming_distance(dhash(increasing), dhash(decreasing)) == 64


def test_phash_is_stable_under_moderate_brightness_change():
    image = textured_image()
    brighter = ImageEnhance.Brightness(image).enhance(1.2)
    assert hamming_distance(phash(image), phash(brighter)) <= 16


def test_hash_to_hex_preserves_expected_width():
    assert len(hash_to_hex(dhash(gradient_image(), hash_size=8))) == 16


def test_hamming_distance_rejects_different_shapes():
    with pytest.raises(ValueError, match="hash shapes must match"):
        hamming_distance(np.zeros((8, 8)), np.zeros((4, 4)))


@pytest.mark.parametrize("algorithm", [dhash, phash])
def test_invalid_hash_size_is_rejected(algorithm):
    with pytest.raises(ValueError, match="hash_size"):
        algorithm(gradient_image(), hash_size=1)
