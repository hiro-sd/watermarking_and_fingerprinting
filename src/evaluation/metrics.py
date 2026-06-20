"""Full-reference image quality metrics."""

import math

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

from watermark.common import ImageInput, load_rgb


def _arrays(reference: ImageInput, candidate: ImageInput) -> tuple[np.ndarray, np.ndarray]:
    first = np.asarray(load_rgb(reference), dtype=np.float64)
    second = np.asarray(load_rgb(candidate), dtype=np.float64)
    if first.shape != second.shape:
        raise ValueError(f"image shapes must match: {first.shape} != {second.shape}")
    return first, second


def psnr(reference: ImageInput, candidate: ImageInput) -> float:
    """Calculate peak signal-to-noise ratio in decibels."""
    first, second = _arrays(reference, candidate)
    mean_squared_error = float(np.mean((first - second) ** 2))
    if mean_squared_error == 0:
        return math.inf
    return 10 * math.log10((255**2) / mean_squared_error)


def ssim(reference: ImageInput, candidate: ImageInput) -> float:
    """Calculate structural similarity over RGB channels."""
    first, second = _arrays(reference, candidate)
    return float(
        structural_similarity(first, second, data_range=255, channel_axis=2)
    )
