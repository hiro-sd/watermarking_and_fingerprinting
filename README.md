# Watermarking & Fingerprinting Benchmark

画像ウォーターマークと知覚フィンガープリントが、圧縮・リサイズ・切り抜きなどの加工にどの程度耐えられるかを比較するための学習プロジェクトです。

現在の実装範囲（Phase 3〜5）:

- dHash（隣接画素の輝度差を利用）
- pHash（DCTの低周波成分を利用）
- ハミング距離による画像間比較
- 2画像を比較するCLI
- LSB方式のウォーターマーク埋め込み・抽出
- DCT方式のウォーターマーク埋め込み・抽出（反復多数決対応）
- JPEG圧縮、リサイズ、中央切り抜き、回転、ノイズ、明るさ変更
- 自動テスト

## セットアップ

```bash
source security/bin/activate
python -m pip install -e '.[dev]'
```

## 使い方

```bash
image-fingerprint path/to/image-a.jpg path/to/image-b.jpg --algorithm phash
image-fingerprint path/to/image-a.jpg path/to/image-b.jpg --algorithm dhash --hash-size 8
```

出力される距離は、0なら同一のフィンガープリントです。値が大きいほど、知覚的な特徴が異なることを表します。類似判定の閾値は、今後の耐性評価実験から決定します。

知覚ハッシュは類似検索のための特徴量であり、暗号学的ハッシュや真正性の証明ではありません。単色・単調な勾配など特徴の乏しい画像や、大幅な切り抜き・回転では判定が不安定になる可能性があります。

## ウォーターマークAPI

```python
from watermark import dct, lsb

marked = lsb.embed(image, b"creator-id")
payload = lsb.extract(marked)

marked = dct.embed(image, b"creator-id", strength=35, repetition=3)
payload = dct.extract(marked, repetition=3)
```

LSB方式はPNGなどの可逆形式でのみ保存してください。JPEG圧縮に弱いことを示す比較基準です。DCT方式の`strength`を上げると耐性が高まる一方、画質劣化も大きくなります。抽出時の`repetition`は埋め込み時と一致させる必要があります。

## 攻撃シミュレーションAPI

```python
from attacks import jpeg_compression, resize, center_crop

compressed = jpeg_compression(image, quality=70)
scaled = resize(image, scale=0.5, restore_size=True)
cropped = center_crop(image, crop_ratio=0.1, restore_size=True)
```

## テスト

```bash
pytest
```

## ディレクトリ

```text
configs/              実験条件
docs/                 設計・調査資料
examples/             サンプル
results/              再生成可能な実験結果
src/attacks/           画像加工処理（今後実装）
src/fingerprint/       知覚フィンガープリント
src/watermark/         ウォーターマーク（今後実装）
tests/                 自動テスト
```
