"""Shared helpers for watermark encoders."""

from functools import lru_cache
from pathlib import Path
from typing import TypeAlias

import numpy as np
from PIL import Image

ImageInput: TypeAlias = str | Path | Image.Image
MAGIC = b"WMK1"
HEADER_SIZE = 8


def load_rgb(image: ImageInput) -> Image.Image:
    """Return an independent RGB copy of an image or image path."""
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    with Image.open(image) as source:
        return source.convert("RGB")


def pack_payload(payload: bytes) -> bytes:
    return MAGIC + len(payload).to_bytes(4, "big") + payload


def unpack_header(header: bytes) -> int:
    if len(header) != HEADER_SIZE or header[:4] != MAGIC:
        raise ValueError("watermark header was not found or is corrupted")
    return int.from_bytes(header[4:], "big")


def bytes_to_bits(value: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(value, dtype=np.uint8))


def bits_to_bytes(bits: np.ndarray) -> bytes:
    array = np.asarray(bits, dtype=np.uint8).reshape(-1)
    if array.size % 8:
        raise ValueError("bit count must be divisible by 8")
    return np.packbits(array).tobytes()


@lru_cache(maxsize=None)
def dct_matrix(size: int = 8) -> np.ndarray:
    positions = np.arange(size, dtype=np.float64)
    frequencies = positions[:, np.newaxis]
    matrix = np.cos(np.pi * (2 * positions + 1) * frequencies / (2 * size))
    matrix[0, :] *= np.sqrt(1 / size)
    matrix[1:, :] *= np.sqrt(2 / size)
    return matrix
