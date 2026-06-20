"""Readable reference implementations of perceptual image hashes."""

from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

import numpy as np
from PIL import Image

ImageInput: TypeAlias = str | Path | Image.Image
HashArray: TypeAlias = np.ndarray


def _load_grayscale(image: ImageInput, size: tuple[int, int]) -> np.ndarray:
    """Load an image, convert it to grayscale, and return float luminance values."""
    if isinstance(image, Image.Image):
        source = image
        should_close = False
    else:
        source = Image.open(image)
        should_close = True

    try:
        resized = source.convert("L").resize(size, Image.Resampling.LANCZOS)
        return np.asarray(resized, dtype=np.float64)
    finally:
        if should_close:
            source.close()


def dhash(image: ImageInput, hash_size: int = 8) -> HashArray:
    """Compute a difference hash from horizontal luminance changes.

    The result contains ``hash_size ** 2`` boolean values. Each bit indicates
    whether a pixel is brighter than the pixel immediately to its right.
    """
    _validate_hash_size(hash_size)
    pixels = _load_grayscale(image, (hash_size + 1, hash_size))
    return pixels[:, :-1] > pixels[:, 1:]


def phash(image: ImageInput, hash_size: int = 8, high_frequency_factor: int = 4) -> HashArray:
    """Compute a perceptual hash using low-frequency 2D-DCT coefficients."""
    _validate_hash_size(hash_size)
    if high_frequency_factor < 1:
        raise ValueError("high_frequency_factor must be at least 1")

    image_size = hash_size * high_frequency_factor
    pixels = _load_grayscale(image, (image_size, image_size))
    dct = _dct_matrix(image_size) @ pixels @ _dct_matrix(image_size).T
    low_frequencies = dct[:hash_size, :hash_size]

    # DC係数は画像全体の平均輝度に支配されるため、閾値の計算から除外する。
    threshold = np.median(low_frequencies.flatten()[1:])
    return low_frequencies > threshold


def hamming_distance(first: HashArray, second: HashArray) -> int:
    """Count differing bits between hashes with identical shapes."""
    first_array = np.asarray(first, dtype=bool)
    second_array = np.asarray(second, dtype=bool)
    if first_array.shape != second_array.shape:
        raise ValueError(
            f"hash shapes must match: {first_array.shape} != {second_array.shape}"
        )
    return int(np.count_nonzero(first_array != second_array))


def hash_to_hex(value: HashArray) -> str:
    """Serialize a boolean hash array as a fixed-width hexadecimal string."""
    bits = np.asarray(value, dtype=bool).reshape(-1)
    bit_string = "".join("1" if bit else "0" for bit in bits)
    width = (len(bit_string) + 3) // 4
    return f"{int(bit_string, 2):0{width}x}"


def _validate_hash_size(hash_size: int) -> None:
    if hash_size < 2:
        raise ValueError("hash_size must be at least 2")


@lru_cache(maxsize=None)
def _dct_matrix(size: int) -> np.ndarray:
    """Create an orthonormal DCT-II transform matrix."""
    positions = np.arange(size, dtype=np.float64)
    frequencies = positions[:, np.newaxis]
    matrix = np.cos(np.pi * (2 * positions + 1) * frequencies / (2 * size))
    matrix[0, :] *= np.sqrt(1 / size)
    matrix[1:, :] *= np.sqrt(2 / size)
    return matrix
