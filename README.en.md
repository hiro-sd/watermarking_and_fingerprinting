# Watermarking & Fingerprinting Robustness Benchmark

[日本語](README.md)

This educational benchmark implements LSB and block-DCT watermarks plus dHash and pHash fingerprints, then evaluates them against six common image transformations. The DCT watermark survived JPEG compression and moderate resizing in this run, but extraction failed after rotation and cropping because the 8×8 block alignment was lost.

The repository also contains a separate `zkp_demo` learning module that demonstrates disclosing an age condition without including the exact age or birth date in the public result.

## Representative results

The current application snapshot contains 200 evaluations over five images: three synthetic samples and two photographs taken by the author. It uses payload `creator-123`, DCT strength 45, and repetition 5.

| Evaluation | Result |
|---|---:|
| DCT: JPEG quality 90 / 70 / 50 / 30 | 100% exact recovery for all settings |
| DCT: resize 75% / 50% | 100% exact recovery |
| DCT: resize 25% | 0% exact recovery |
| DCT: crop 5% / 10% / 20% | 0% exact recovery for all settings |
| DCT: rotation 1° / 5° / 15° | 0% exact recovery for all settings |
| Unmodified DCT-marked image quality | Mean PSNR 39.63 dB, mean SSIM 0.946 |

Five images are enough to validate the pipeline but not to establish general performance. Synchronization after geometric edits, bit error rate, and ROC evaluation with non-matching image pairs remain open work. The committed [generated report](results/application_snapshot/report.md) and [summary CSV](results/application_snapshot/summary.csv) are the single detailed record of these figures.

![Exact watermark recovery rate](results/application_snapshot/watermark_detection_rate.png)

## Quick reproduction

```bash
python3 -m venv security
source security/bin/activate
python -m pip install -e '.[dev]'
python examples/generate_samples.py
watermark-benchmark --config configs/default.yaml
pytest
```

`examples/generate_samples.py` creates the three redistributable synthetic samples. The application snapshot also used two private photographs, so a run using only the public repository will have a different image count and aggregate values.

## Research questions

1. How do LSB and block-DCT watermark recovery rates differ after image processing?
2. What trade-off exists between robustness and image quality measured by PSNR and SSIM?
3. How do dHash and pHash Hamming distances change across attack types and strengths?

## Threat model

The benchmark models routine transformations applied while redistributing visually similar content:

- JPEG recompression
- downscaling followed by restoration to the original size
- center cropping followed by restoration to the original size
- rotation
- Gaussian noise
- brightness adjustment

It does not model key compromise, generative reconstruction, advanced synchronization attacks, or cryptographic proof of authorship. This is an educational implementation, not a production DRM system or an automated copyright-infringement detector.

## Implemented methods

| Category | Method | Purpose |
|---|---|---|
| Watermark | LSB | Fragile baseline that stores a framed payload in pixel least-significant bits |
| Watermark | block-DCT | Blind watermark using repeated relationships between mid-frequency coefficients |
| Fingerprint | dHash | 64-bit representation of neighboring luminance differences |
| Fingerprint | pHash | 64-bit representation derived from low-frequency DCT coefficients |

The DCT implementation repeats each bit an odd number of times and uses majority voting during extraction. Increasing `strength` may improve robustness but also increases visible distortion.

## Processing flow

```text
input image ──┬── embed watermark ── simulate attack ── extract payload
              │                              │
              └── source perceptual hash ────┼── Hamming distance
                                             │
source image ────────────────────────────────┴── PSNR / SSIM
```

Each run writes image-level measurements, aggregated data, plots, and a Markdown report to `results/default/`.

## Committed application snapshot

`results/application_snapshot/` contains only the representative configuration, aggregates, generated report, and plots. Source photographs and per-image intermediate results are not committed.

- [Configuration](results/application_snapshot/config.yaml)
- [Generated report for all 40 conditions](results/application_snapshot/report.md)
- [Summary CSV](results/application_snapshot/summary.csv)
- [Exact watermark recovery plot](results/application_snapshot/watermark_detection_rate.png)
- [Perceptual fingerprint distance plot](results/application_snapshot/fingerprint_distance.png)
- [PSNR and SSIM plot](results/application_snapshot/image_quality.png)

LSB recovered the payload only from unmodified images and failed after every tested transformation. DCT was comparatively robust to JPEG compression, moderate resizing, noise, and brightness changes, but failed after cropping and rotation because extraction depends on the original 8×8 block alignment.

## CLI and API

Compare two perceptual fingerprints:

```bash
image-fingerprint image-a.jpg image-b.jpg --algorithm phash
image-fingerprint image-a.jpg image-b.jpg --algorithm dhash --hash-size 8
```

Use the watermark API directly:

```python
from attacks import jpeg_compression
from watermark import dct, lsb

marked = dct.embed(image, b"creator-id", strength=45, repetition=5)
attacked = jpeg_compression(marked, quality=70)
payload = dct.extract(attacked, repetition=5)

fragile = lsb.embed(image, b"creator-id")
payload = lsb.extract(fragile)
```

LSB-marked images must be stored in a lossless format such as PNG. JPEG encoding normally destroys the embedded header and payload.

## Metrics

- Exact recovery rate: fraction of samples where every extracted payload byte matches
- PSNR: pixel-error measure where a higher value means less distortion
- SSIM: structural similarity measure where a value closer to 1 means greater similarity
- Hamming distance: number of differing bits between two 64-bit perceptual hashes

No fixed fingerprint threshold is used because it must be calibrated with both matching and non-matching image pairs, then evaluated using false-positive and false-negative rates.

## ZKP age-condition concept demo

```bash
age-proof-demo \
  --birth-date 2000-01-01 \
  --minimum-age 20 \
  --reference-date 2026-08-11
```

> **Important:** This is not a real cryptographic zero-knowledge proof. It is an educational HMAC-based attestation created by a trusted issuer. It has no cryptographic range proof, formal zero-knowledge guarantee, or production key management and must not be used for real identity or age verification.

See the [Japanese ZKP learning notes](docs/zkp_notes.md) for terminology, roles, and limitations.

## Current limitations

- DCT extraction depends on 8×8 block alignment and is vulnerable to cropping and rotation.
- Repetition voting is simple redundancy, not an error-correcting code such as BCH or Reed–Solomon.
- Payloads are neither encrypted nor signed and do not prove ownership.
- The five-image snapshot is too small for statistical conclusions.
- Semantic similarity and generative-image edits are outside the current benchmark.

Future work includes a redistributable evaluation dataset, error-correcting codes, synchronization markers, confidence intervals, and ROC analysis with non-matching image pairs.
