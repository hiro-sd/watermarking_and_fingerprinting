"""Generate deterministic, license-free synthetic benchmark images."""

from pathlib import Path

import numpy as np
from PIL import Image

OUTPUT = Path(__file__).parent / "images"
SIZE = 256


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    y, x = np.indices((SIZE, SIZE))

    waves = np.stack(
        (
            120 + 80 * np.sin(x / 13),
            120 + 70 * np.cos(y / 17),
            120 + 75 * np.sin((x + y) / 21),
        ),
        axis=-1,
    )
    checker = np.stack(
        (
            50 + 170 * ((x // 24 + y // 24) % 2),
            70 + 150 * ((x // 32) % 2),
            80 + 140 * ((y // 32) % 2),
        ),
        axis=-1,
    )
    radius = np.sqrt((x - SIZE / 2) ** 2 + (y - SIZE / 2) ** 2)
    radial = np.stack(
        (
            128 + 90 * np.sin(radius / 8),
            128 + 80 * np.cos(radius / 12),
            128 + 70 * np.sin(np.arctan2(y - 128, x - 128) * 8),
        ),
        axis=-1,
    )

    for name, pixels in {
        "waves": waves,
        "checker": checker,
        "radial": radial,
    }.items():
        Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8), "RGB").save(
            OUTPUT / f"{name}.png"
        )
    print(f"generated 3 images in {OUTPUT}")


if __name__ == "__main__":
    main()
