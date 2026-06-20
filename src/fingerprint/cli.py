"""Command-line interface for comparing image fingerprints."""

import argparse
from collections.abc import Sequence

from .hashing import dhash, hamming_distance, hash_to_hex, phash


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two images using a perceptual fingerprint."
    )
    parser.add_argument("first", help="path to the first image")
    parser.add_argument("second", help="path to the second image")
    parser.add_argument(
        "--algorithm",
        choices=("dhash", "phash"),
        default="phash",
        help="fingerprint algorithm (default: phash)",
    )
    parser.add_argument(
        "--hash-size",
        type=int,
        default=8,
        help="hash side length; total bits are size squared (default: 8)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    algorithm = dhash if args.algorithm == "dhash" else phash
    first_hash = algorithm(args.first, hash_size=args.hash_size)
    second_hash = algorithm(args.second, hash_size=args.hash_size)
    distance = hamming_distance(first_hash, second_hash)

    print(f"algorithm: {args.algorithm}")
    print(f"first:     {hash_to_hex(first_hash)}")
    print(f"second:    {hash_to_hex(second_hash)}")
    print(f"distance:  {distance}/{first_hash.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
