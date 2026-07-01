from __future__ import annotations

import argparse

from market_opportunity.config import SETTINGS
from market_opportunity.pipeline import ingest, train


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Market opportunity prediction engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Load CSVs or generate demo data into SQLite")
    ingest_parser.add_argument("--seed", type=int, default=42)

    train_parser = subparsers.add_parser("train", help="Train and evaluate the opportunity model")
    train_parser.add_argument("--seed", type=int, default=42)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        ingest(settings=SETTINGS, seed=args.seed)
        print(f"Database ready: {SETTINGS.database_path}")
    elif args.command == "train":
        result = train(settings=SETTINGS, seed=args.seed)
        print("Training complete")
        print(result.metrics.to_string(index=False))
        print(f"Predictions: {SETTINGS.predictions_csv}")
        print(f"Model: {SETTINGS.model_path}")


if __name__ == "__main__":
    main()
