# Watermarking & Fingerprinting Robustness Benchmark

[日本語](README.md)

This project provides a reproducible benchmark for measuring how image watermarks and perceptual fingerprints behave under common image transformations.

## Research questions

1. How do LSB and block-DCT watermark recovery rates differ after image processing?
2. What trade-off exists between robustness and image quality measured by PSNR and SSIM?
3. How do dHash and pHash Hamming distances change across attack types and strengths?

## Implemented methods

- Fragile LSB watermark with a framed byte payload
- Blind block-DCT watermark with repetition and majority voting
- dHash and pHash perceptual fingerprints
- JPEG compression, resizing, center cropping, rotation, Gaussian noise, and brightness attacks
- Exact payload recovery rate, PSNR, SSIM, and fingerprint distance
- CSV, PNG chart, and Markdown report generation

## Threat model

The benchmark models routine transformations applied while redistributing visually similar content. It does not model key compromise, generative reconstruction, advanced synchronization attacks, or cryptographic proof of authorship. This is an educational implementation, not a production DRM system.

## Setup and reproduction

```bash
python3 -m venv security
source security/bin/activate
python -m pip install -e '.[dev]'
python examples/generate_samples.py
watermark-benchmark --config configs/default.yaml
pytest
```

Results are written to `results/default/`:

- `raw_results.csv`
- `summary.csv`
- `report.md`
- `watermark_detection_rate.png`
- `fingerprint_distance.png`
- `image_quality.png`

## Initial run

The reproducibility run evaluated 120 combinations over three synthetic images using payload `creator-123`, DCT strength 45, and repetition 5. LSB recovered only the unmodified images. DCT recovered all payloads after JPEG qualities 90/70/50/30, resize scales 0.75/0.5, Gaussian noise sigma 2/5/10, and brightness factors 0.7/1.1. It failed after cropping, rotation, and resize scale 0.25; brightness 1.3 recovered two of three payloads. The unmodified DCT-marked images averaged 36.70 dB PSNR and 0.912 SSIM.

These figures validate the pipeline on a small synthetic set; they are not a general performance claim.

![Exact watermark recovery rate](docs/assets/watermark_detection_rate.png)

![Perceptual fingerprint distance](docs/assets/fingerprint_distance.png)

![PSNR and SSIM](docs/assets/image_quality.png)

Use your own licensed images by changing `dataset_dir` in `configs/default.yaml`.

## Interpretation

An exact recovery rate of 1 means every payload byte was recovered. Higher PSNR and SSIM indicate less visual distortion. Lower dHash and pHash distances indicate a more stable perceptual fingerprint. A similarity threshold is intentionally not hard-coded because it must be calibrated against both matching and non-matching image pairs.

## Limitations

- Block alignment is not synchronized after geometric attacks.
- Repetition voting is not a full error-correcting code.
- Payloads are neither encrypted nor signed.
- The synthetic sample set validates the pipeline but is too small for general conclusions.
- Semantic or generative edits are outside the current scope.
