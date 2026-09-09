"""Configuration-driven robustness benchmark."""

import argparse
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from PIL import Image

from attacks import (
    brightness,
    center_crop,
    gaussian_noise,
    jpeg_compression,
    resize,
    rotate,
)
from fingerprint import dhash, hamming_distance, phash
from watermark import dct, lsb

from .metrics import psnr, ssim
from .plots import create_plots

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
ATTACKS: dict[str, Callable[..., Image.Image]] = {
    "jpeg": jpeg_compression,
    "resize": resize,
    "crop": center_crop,
    "rotate": rotate,
    "noise": gaussian_noise,
    "brightness": brightness,
}


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError("configuration root must be a mapping")
    return config


def run_benchmark(config_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run every image/watermark/attack combination from a YAML configuration."""
    config_path = Path(config_path).resolve()
    config = load_config(config_path)
    root = config_path.parent.parent
    dataset_dir = _resolve(root, config.get("dataset_dir", "examples/images"))
    output_dir = _resolve(root, config.get("output_dir", "results/default"))
    images = _image_paths(dataset_dir)
    payload = str(config.get("payload", "creator-123")).encode("utf-8")

    rows: list[dict[str, Any]] = []
    for image_path in images:
        with Image.open(image_path) as source:
            original = source.convert("RGB")
        for watermark_name, watermark_params in config["watermarks"].items():
            marked = _embed(watermark_name, original, payload, watermark_params)
            for attack in _attack_variants(config["attacks"]):
                attacked = _apply_attack(marked, attack)
                recovered, error = _recover(
                    watermark_name, attacked, payload, watermark_params
                )
                original_dhash = dhash(original)
                original_phash = phash(original)
                rows.append(
                    {
                        "image": image_path.name,
                        "watermark": watermark_name,
                        "attack": attack["name"],
                        "attack_label": _attack_label(attack),
                        "parameters": json.dumps(attack["params"], sort_keys=True),
                        "detection_success": recovered,
                        "extraction_error": error,
                        "psnr": psnr(original, attacked),
                        "ssim": ssim(original, attacked),
                        "dhash_distance": hamming_distance(
                            original_dhash, dhash(attacked)
                        ),
                        "phash_distance": hamming_distance(
                            original_phash, phash(attacked)
                        ),
                    }
                )

    raw = pd.DataFrame(rows)
    summary = _summarize(raw)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(output_dir / "raw_results.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    create_plots(summary, output_dir)
    _write_report(config_path, dataset_dir, raw, summary, output_dir, root)
    return raw, summary


def _embed(
    name: str, image: Image.Image, payload: bytes, params: dict[str, Any]
) -> Image.Image:
    if name == "lsb":
        return lsb.embed(image, payload)
    if name == "dct":
        return dct.embed(image, payload, **params)
    raise ValueError(f"unknown watermark: {name}")


def _recover(
    name: str,
    image: Image.Image,
    expected: bytes,
    params: dict[str, Any],
) -> tuple[bool, str]:
    try:
        if name == "lsb":
            payload = lsb.extract(image)
        elif name == "dct":
            payload = dct.extract(
                image,
                repetition=int(params.get("repetition", 3)),
                max_payload_size=len(expected),
            )
        else:
            raise ValueError(f"unknown watermark: {name}")
        return payload == expected, "" if payload == expected else "payload_mismatch"
    except ValueError as error:
        return False, type(error).__name__


def _attack_variants(entries: list[dict[str, Any]]):
    yield {"name": "none", "params": {}}
    for entry in entries:
        name = entry["name"]
        if name not in ATTACKS:
            raise ValueError(f"unknown attack: {name}")
        variants = entry.get("variants", [{}])
        for params in variants:
            yield {"name": name, "params": dict(params)}


def _apply_attack(image: Image.Image, attack: dict[str, Any]) -> Image.Image:
    if attack["name"] == "none":
        return image.copy()
    return ATTACKS[attack["name"]](image, **attack["params"])


def _attack_label(attack: dict[str, Any]) -> str:
    if not attack["params"]:
        return attack["name"]
    values = ",".join(f"{key}={value}" for key, value in attack["params"].items())
    return f"{attack['name']}:{values}"


def _summarize(raw: pd.DataFrame) -> pd.DataFrame:
    return (
        raw.groupby(["watermark", "attack_label"], sort=False)
        .agg(
            samples=("image", "count"),
            detection_rate=("detection_success", "mean"),
            mean_psnr=("psnr", "mean"),
            mean_ssim=("ssim", "mean"),
            mean_dhash_distance=("dhash_distance", "mean"),
            mean_phash_distance=("phash_distance", "mean"),
        )
        .reset_index()
    )


def _image_paths(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ValueError(
            f"dataset directory does not exist: {directory}. "
            "Run examples/generate_samples.py first."
        )
    paths = sorted(
        path for path in directory.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not paths:
        raise ValueError(f"no supported images found in: {directory}")
    return paths


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _write_report(
    config_path: Path,
    dataset_dir: Path,
    raw: pd.DataFrame,
    summary: pd.DataFrame,
    output_dir: Path,
    root: Path,
) -> None:
    table = _markdown_table(summary.round(4))
    display_config = _display_path(config_path, root)
    display_dataset = _display_path(dataset_dir, root)
    report = f"""# Benchmark report

- Configuration: `{display_config}`
- Dataset: `{display_dataset}`
- Images: {raw['image'].nunique()}
- Evaluations: {len(raw)}

## Summary

{table}

`detection_rate` is exact payload recovery. PSNR and SSIM compare each attacked,
watermarked image against its unwatermarked source.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")


def _display_path(path: Path, root: Path) -> str:
    """Prefer a repository-relative path in generated public reports."""

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _markdown_table(frame: pd.DataFrame) -> str:
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run watermark robustness benchmark")
    parser.add_argument(
        "--config", default="configs/default.yaml", help="YAML configuration path"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw, summary = run_benchmark(args.config)
    print(f"completed {len(raw)} evaluations ({len(summary)} summary rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
