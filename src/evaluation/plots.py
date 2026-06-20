"""Plot benchmark summaries without requiring a display server."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def create_plots(summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _detection_plot(summary, output_dir / "watermark_detection_rate.png")
    _fingerprint_plot(summary, output_dir / "fingerprint_distance.png")
    _quality_plot(summary, output_dir / "image_quality.png")


def _detection_plot(summary: pd.DataFrame, path: Path) -> None:
    pivot = summary.pivot(
        index="attack_label", columns="watermark", values="detection_rate"
    )
    axis = pivot.plot(kind="bar", figsize=(12, 5), ylim=(0, 1.05))
    axis.set_title("Exact watermark recovery rate")
    axis.set_xlabel("Attack")
    axis.set_ylabel("Recovery rate")
    axis.legend(title="Watermark")
    axis.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def _fingerprint_plot(summary: pd.DataFrame, path: Path) -> None:
    grouped = summary.groupby("attack_label", sort=False)[
        ["mean_dhash_distance", "mean_phash_distance"]
    ].mean()
    axis = grouped.plot(kind="bar", figsize=(12, 5))
    axis.set_title("Mean perceptual fingerprint distance (64 bits)")
    axis.set_xlabel("Attack")
    axis.set_ylabel("Hamming distance")
    axis.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def _quality_plot(summary: pd.DataFrame, path: Path) -> None:
    grouped = summary.groupby("attack_label", sort=False)[
        ["mean_psnr", "mean_ssim"]
    ].mean()
    figure, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    grouped["mean_psnr"].plot(kind="bar", ax=axes[0], color="#4472C4")
    grouped["mean_ssim"].plot(kind="bar", ax=axes[1], color="#70AD47")
    axes[0].set_title("Mean image quality after watermarking and attack")
    axes[0].set_ylabel("PSNR (dB)")
    axes[1].set_ylabel("SSIM")
    axes[1].set_xlabel("Attack")
    axes[1].set_ylim(0, 1.05)
    for axis in axes:
        axis.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close(figure)
