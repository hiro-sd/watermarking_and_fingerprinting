import numpy as np
import pytest

from attacks import jpeg_compression
from watermark import dct, lsb

from helpers import textured_rgb_image


def test_lsb_round_trip():
    image = textured_rgb_image(64)
    marked = lsb.embed(image, b"creator-123")
    assert lsb.extract(marked) == b"creator-123"
    assert np.max(
        np.abs(np.asarray(marked, dtype=int) - np.asarray(image, dtype=int))
    ) <= 1


def test_lsb_rejects_oversized_payload():
    image = textured_rgb_image(8)
    with pytest.raises(ValueError, match="too large"):
        lsb.embed(image, b"x" * (lsb.capacity(image) + 1))


def test_lsb_is_fragile_under_jpeg_compression():
    marked = lsb.embed(textured_rgb_image(128), b"fragile")
    attacked = jpeg_compression(marked, quality=90)
    with pytest.raises(ValueError, match="header"):
        lsb.extract(attacked)


def test_dct_round_trip():
    payload = b"creator-123"
    marked = dct.embed(textured_rgb_image(), payload, strength=35, repetition=3)
    assert dct.extract(marked, repetition=3) == payload


def test_dct_survives_moderate_jpeg_compression():
    payload = b"sony"
    marked = dct.embed(textured_rgb_image(), payload, strength=45, repetition=5)
    attacked = jpeg_compression(marked, quality=85)
    assert dct.extract(attacked, repetition=5) == payload


def test_dct_rejects_even_repetition():
    with pytest.raises(ValueError, match="odd"):
        dct.embed(textured_rgb_image(), b"x", repetition=2)
