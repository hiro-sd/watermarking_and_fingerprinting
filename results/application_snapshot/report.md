# Benchmark report

- Configuration: `configs/default.yaml`
- Dataset: `examples/images`
- Images: 5
- Evaluations: 200

## Summary

| watermark | attack_label | samples | detection_rate | mean_psnr | mean_ssim | mean_dhash_distance | mean_phash_distance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| lsb | none | 5 | 1.0 | 90.0507 | 1.0 | 0.0 | 0.0 |
| lsb | jpeg:quality=90 | 5 | 0.0 | 40.7504 | 0.942 | 0.2 | 0.4 |
| lsb | jpeg:quality=70 | 5 | 0.0 | 35.8957 | 0.908 | 0.0 | 1.2 |
| lsb | jpeg:quality=50 | 5 | 0.0 | 34.1636 | 0.8816 | 0.6 | 0.8 |
| lsb | jpeg:quality=30 | 5 | 0.0 | 32.0812 | 0.8438 | 0.0 | 1.2 |
| lsb | resize:scale=0.75 | 5 | 0.0 | 43.6254 | 0.9628 | 0.0 | 0.4 |
| lsb | resize:scale=0.5 | 5 | 0.0 | 39.8577 | 0.9114 | 0.2 | 1.2 |
| lsb | resize:scale=0.25 | 5 | 0.0 | 35.9118 | 0.831 | 0.0 | 0.8 |
| lsb | crop:crop_ratio=0.05 | 5 | 0.0 | 14.8636 | 0.5479 | 7.8 | 13.2 |
| lsb | crop:crop_ratio=0.1 | 5 | 0.0 | 12.3524 | 0.4363 | 18.4 | 19.6 |
| lsb | crop:crop_ratio=0.2 | 5 | 0.0 | 10.9396 | 0.4008 | 33.6 | 32.8 |
| lsb | rotate:angle=1 | 5 | 0.0 | 21.2151 | 0.7363 | 2.2 | 7.2 |
| lsb | rotate:angle=5 | 5 | 0.0 | 14.7004 | 0.5924 | 8.8 | 16.4 |
| lsb | rotate:angle=15 | 5 | 0.0 | 10.9688 | 0.4104 | 20.8 | 25.6 |
| lsb | noise:sigma=2,seed=42 | 5 | 0.0 | 42.0099 | 0.9689 | 0.0 | 1.6 |
| lsb | noise:sigma=5,seed=42 | 5 | 0.0 | 34.1272 | 0.847 | 0.4 | 2.0 |
| lsb | noise:sigma=10,seed=42 | 5 | 0.0 | 28.1253 | 0.627 | 0.4 | 3.2 |
| lsb | brightness:factor=0.7 | 5 | 0.0 | 16.0792 | 0.909 | 1.2 | 1.6 |
| lsb | brightness:factor=1.1 | 5 | 0.0 | 26.0002 | 0.9922 | 0.8 | 1.6 |
| lsb | brightness:factor=1.3 | 5 | 0.0 | 17.5912 | 0.9348 | 0.6 | 1.2 |
| dct | none | 5 | 1.0 | 39.6335 | 0.9456 | 0.0 | 1.2 |
| dct | jpeg:quality=90 | 5 | 1.0 | 35.4944 | 0.8959 | 0.0 | 1.6 |
| dct | jpeg:quality=70 | 5 | 1.0 | 32.8993 | 0.8531 | 0.4 | 1.6 |
| dct | jpeg:quality=50 | 5 | 1.0 | 32.316 | 0.8411 | 0.2 | 1.2 |
| dct | jpeg:quality=30 | 5 | 1.0 | 29.8196 | 0.7584 | 0.8 | 2.4 |
| dct | resize:scale=0.75 | 5 | 1.0 | 35.6103 | 0.9181 | 0.0 | 1.6 |
| dct | resize:scale=0.5 | 5 | 1.0 | 34.5323 | 0.887 | 0.0 | 2.0 |
| dct | resize:scale=0.25 | 5 | 0.0 | 33.885 | 0.8305 | 0.0 | 1.6 |
| dct | crop:crop_ratio=0.05 | 5 | 0.0 | 14.8377 | 0.5072 | 7.8 | 14.0 |
| dct | crop:crop_ratio=0.1 | 5 | 0.0 | 12.3431 | 0.4015 | 19.0 | 20.0 |
| dct | crop:crop_ratio=0.2 | 5 | 0.0 | 10.939 | 0.3668 | 33.6 | 33.2 |
| dct | rotate:angle=1 | 5 | 0.0 | 21.0648 | 0.6822 | 2.2 | 6.8 |
| dct | rotate:angle=5 | 5 | 0.0 | 14.6763 | 0.5484 | 8.8 | 16.4 |
| dct | rotate:angle=15 | 5 | 0.0 | 10.9608 | 0.3802 | 21.0 | 25.2 |
| dct | noise:sigma=2,seed=42 | 5 | 1.0 | 37.3038 | 0.9193 | 0.0 | 1.6 |
| dct | noise:sigma=5,seed=42 | 5 | 1.0 | 32.8105 | 0.8138 | 0.4 | 2.4 |
| dct | noise:sigma=10,seed=42 | 5 | 1.0 | 27.7419 | 0.6132 | 0.6 | 3.2 |
| dct | brightness:factor=0.7 | 5 | 1.0 | 15.8881 | 0.8753 | 1.2 | 2.0 |
| dct | brightness:factor=1.1 | 5 | 1.0 | 26.6494 | 0.9317 | 0.6 | 2.0 |
| dct | brightness:factor=1.3 | 5 | 0.8 | 17.8759 | 0.887 | 0.6 | 2.4 |

`detection_rate` is exact payload recovery. PSNR and SSIM compare each attacked,
watermarked image against its unwatermarked source.
