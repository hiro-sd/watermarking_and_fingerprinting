import math

import numpy as np
import pytest
from PIL import Image

from evaluation.metrics import psnr, ssim

from helpers import textured_rgb_image


def test_identical_images_have_perfect_quality():
    image = textured_rgb_image(64)
    assert math.isinf(psnr(image, image.copy()))
    assert ssim(image, image.copy()) == pytest.approx(1.0)


def test_changed_image_has_finite_quality_scores():
    image = textured_rgb_image(64)
    changed_pixels = np.clip(np.asarray(image, dtype=int) + 10, 0, 255).astype(np.uint8)
    changed = Image.fromarray(changed_pixels, "RGB")
    assert 20 < psnr(image, changed) < 40
    assert 0 < ssim(image, changed) < 1


def test_metrics_reject_different_shapes():
    with pytest.raises(ValueError, match="shapes must match"):
        psnr(textured_rgb_image(32), textured_rgb_image(64))
