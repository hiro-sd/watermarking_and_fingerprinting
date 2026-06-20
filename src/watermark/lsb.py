"""Least-significant-bit watermark used as a fragile baseline."""

import numpy as np
from PIL import Image

from .common import (
    HEADER_SIZE,
    ImageInput,
    bits_to_bytes,
    bytes_to_bits,
    load_rgb,
    pack_payload,
    unpack_header,
)


def capacity(image: ImageInput) -> int:
    """Return the maximum payload size in bytes, excluding the header."""
    rgb = load_rgb(image)
    return max(0, (rgb.width * rgb.height * 3) // 8 - HEADER_SIZE)


def embed(image: ImageInput, payload: bytes) -> Image.Image:
    """Embed arbitrary bytes in RGB channel least-significant bits."""
    rgb = load_rgb(image)
    if len(payload) > capacity(rgb):
        raise ValueError(
            f"payload is too large: {len(payload)} bytes; capacity is {capacity(rgb)}"
        )

    pixels = np.asarray(rgb, dtype=np.uint8).copy()
    flat = pixels.reshape(-1)
    bits = bytes_to_bits(pack_payload(payload))
    flat[: bits.size] = (flat[: bits.size] & 0xFE) | bits
    return Image.fromarray(pixels, mode="RGB")


def extract(image: ImageInput) -> bytes:
    """Extract bytes from an unmodified lossless LSB-watermarked image."""
    rgb = load_rgb(image)
    bits = (np.asarray(rgb, dtype=np.uint8).reshape(-1) & 1).astype(np.uint8)
    header_bits = HEADER_SIZE * 8
    if bits.size < header_bits:
        raise ValueError("image is too small to contain a watermark header")

    payload_size = unpack_header(bits_to_bytes(bits[:header_bits]))
    if payload_size > capacity(rgb):
        raise ValueError("watermark declares a payload larger than image capacity")
    end = header_bits + payload_size * 8
    return bits_to_bytes(bits[header_bits:end])
