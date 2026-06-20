# Watermarking & Fingerprinting Benchmark

画像ウォーターマークと知覚フィンガープリントが、圧縮・リサイズ・切り抜きなどの加工にどの程度耐えられるかを比較するための学習プロジェクトです。

現在の実装範囲（Phase 3）:

- dHash（隣接画素の輝度差を利用）
- pHash（DCTの低周波成分を利用）
- ハミング距離による画像間比較
- 2画像を比較するCLI
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
