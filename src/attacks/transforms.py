"""Controlled image transformations used as watermark robustness attacks."""

from io import BytesIO

import numpy as np
from PIL import Image, ImageEnhance

from watermark.common import ImageInput, load_rgb


def jpeg_compression(image: ImageInput, quality: int = 75) -> Image.Image:
    """Round-trip an image through JPEG encoding at a selected quality."""
    if not 1 <= quality <= 100:
        raise ValueError("quality must be between 1 and 100")
    rgb = load_rgb(image)
    buffer = BytesIO()
    rgb.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    with Image.open(buffer) as compressed:
        return compressed.convert("RGB")


def resize(
    image: ImageInput, scale: float = 0.5, *, restore_size: bool = True
) -> Image.Image:
    """Scale an image and optionally restore its original dimensions."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    rgb = load_rgb(image)
    original_size = rgb.size
    scaled_size = (
        max(1, round(rgb.width * scale)),
        max(1, round(rgb.height * scale)),
    )
    result = rgb.resize(scaled_size, Image.Resampling.LANCZOS)
    if restore_size:
        result = result.resize(original_size, Image.Resampling.LANCZOS)
    return result


def center_crop(
    image: ImageInput, crop_ratio: float = 0.1, *, restore_size: bool = True
) -> Image.Image:
    """Remove an equal ratio from each edge and optionally restore dimensions."""
    if not 0 <= crop_ratio < 0.5:
        raise ValueError("crop_ratio must be at least 0 and less than 0.5")
    rgb = load_rgb(image)
    original_size = rgb.size
    x_margin = round(rgb.width * crop_ratio)
    y_margin = round(rgb.height * crop_ratio)
    result = rgb.crop(
        (x_margin, y_margin, rgb.width - x_margin, rgb.height - y_margin)
    )
    if restore_size:
        result = result.resize(original_size, Image.Resampling.LANCZOS)
    return result


def rotate(image: ImageInput, angle: float = 5.0) -> Image.Image:
    """Rotate around the center while preserving dimensions."""
    rgb = load_rgb(image)
    return rgb.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=False,
        fillcolor=(0, 0, 0),
    )


def gaussian_noise(
    image: ImageInput, sigma: float = 5.0, *, seed: int | None = None
) -> Image.Image:
    """Add reproducible zero-mean Gaussian noise to RGB values."""
    if sigma < 0:
        raise ValueError("sigma must not be negative")
    pixels = np.asarray(load_rgb(image), dtype=np.float64)
    noise = np.random.default_rng(seed).normal(0, sigma, size=pixels.shape)
    result = np.clip(np.rint(pixels + noise), 0, 255).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")


def brightness(image: ImageInput, factor: float = 1.2) -> Image.Image:
    """Multiply image brightness by a non-negative factor."""
    if factor < 0:
        raise ValueError("factor must not be negative")
    return ImageEnhance.Brightness(load_rgb(image)).enhance(factor)
