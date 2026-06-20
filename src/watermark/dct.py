"""Blind block-DCT watermark with majority-vote repetition."""

import numpy as np
from PIL import Image

from .common import (
    HEADER_SIZE,
    ImageInput,
    bits_to_bytes,
    bytes_to_bits,
    dct_matrix,
    load_rgb,
    pack_payload,
    unpack_header,
)

BLOCK_SIZE = 8
COEFFICIENT_A = (3, 2)
COEFFICIENT_B = (2, 3)


def capacity(image: ImageInput, repetition: int = 3) -> int:
    """Return payload capacity in bytes for the supplied repetition count."""
    _validate_parameters(strength=1, repetition=repetition)
    rgb = load_rgb(image)
    blocks = (rgb.width // BLOCK_SIZE) * (rgb.height // BLOCK_SIZE)
    usable_bytes = blocks // repetition // 8
    return max(0, usable_bytes - HEADER_SIZE)


def embed(
    image: ImageInput,
    payload: bytes,
    *,
    strength: float = 30.0,
    repetition: int = 3,
) -> Image.Image:
    """Embed bytes by ordering two mid-frequency DCT coefficients per block."""
    _validate_parameters(strength, repetition)
    rgb = load_rgb(image)
    available = capacity(rgb, repetition)
    if len(payload) > available:
        raise ValueError(
            f"payload is too large: {len(payload)} bytes; capacity is {available}"
        )

    ycbcr = np.asarray(rgb.convert("YCbCr"), dtype=np.float64).copy()
    luminance = ycbcr[:, :, 0]
    bits = np.repeat(bytes_to_bits(pack_payload(payload)), repetition)
    transform = dct_matrix(BLOCK_SIZE)

    for bit, (row, column) in zip(bits, _block_positions(luminance.shape)):
        block = luminance[row : row + BLOCK_SIZE, column : column + BLOCK_SIZE]
        coefficients = transform @ block @ transform.T
        first = coefficients[COEFFICIENT_A]
        second = coefficients[COEFFICIENT_B]
        signed_difference = first - second if bit else second - first
        if signed_difference < strength:
            adjustment = (strength - signed_difference) / 2
            if bit:
                coefficients[COEFFICIENT_A] += adjustment
                coefficients[COEFFICIENT_B] -= adjustment
            else:
                coefficients[COEFFICIENT_A] -= adjustment
                coefficients[COEFFICIENT_B] += adjustment
        restored = transform.T @ coefficients @ transform
        luminance[row : row + BLOCK_SIZE, column : column + BLOCK_SIZE] = restored

    ycbcr[:, :, 0] = np.clip(np.rint(luminance), 0, 255)
    return Image.fromarray(ycbcr.astype(np.uint8), mode="YCbCr").convert("RGB")


def extract(
    image: ImageInput,
    *,
    repetition: int = 3,
    max_payload_size: int | None = None,
) -> bytes:
    """Extract a repeated DCT watermark without needing the original image."""
    _validate_parameters(strength=1, repetition=repetition)
    rgb = load_rgb(image)
    luminance = np.asarray(rgb.convert("YCbCr"), dtype=np.float64)[:, :, 0]
    available = capacity(rgb, repetition)
    positions = list(_block_positions(luminance.shape))

    header = _extract_bytes(luminance, positions, HEADER_SIZE, repetition)
    payload_size = unpack_header(header)
    limit = available if max_payload_size is None else min(available, max_payload_size)
    if payload_size > limit:
        raise ValueError(
            f"watermark payload size {payload_size} exceeds allowed capacity {limit}"
        )
    combined = _extract_bytes(
        luminance, positions, HEADER_SIZE + payload_size, repetition
    )
    return combined[HEADER_SIZE:]


def _extract_bytes(
    luminance: np.ndarray,
    positions: list[tuple[int, int]],
    byte_count: int,
    repetition: int,
) -> bytes:
    required_blocks = byte_count * 8 * repetition
    if required_blocks > len(positions):
        raise ValueError("image does not contain enough blocks for the watermark")

    transform = dct_matrix(BLOCK_SIZE)
    raw_bits = []
    for row, column in positions[:required_blocks]:
        block = luminance[row : row + BLOCK_SIZE, column : column + BLOCK_SIZE]
        coefficients = transform @ block @ transform.T
        raw_bits.append(coefficients[COEFFICIENT_A] > coefficients[COEFFICIENT_B])

    votes = np.asarray(raw_bits, dtype=np.uint8).reshape(-1, repetition)
    decoded = votes.sum(axis=1) > repetition // 2
    return bits_to_bytes(decoded)


def _block_positions(shape: tuple[int, ...]):
    height, width = shape[:2]
    for row in range(0, height - BLOCK_SIZE + 1, BLOCK_SIZE):
        for column in range(0, width - BLOCK_SIZE + 1, BLOCK_SIZE):
            yield row, column


def _validate_parameters(strength: float, repetition: int) -> None:
    if strength <= 0:
        raise ValueError("strength must be positive")
    if repetition < 1 or repetition % 2 == 0:
        raise ValueError("repetition must be a positive odd integer")
