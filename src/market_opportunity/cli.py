from __future__ import annotations

import argparse

from market_opportunity.config import SETTINGS
from market_opportunity.pipeline import ingest, train


def add_data_arguments(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument(
        "--source",
        choices=["real", "csv", "synthetic"],
        default="real",
        help="Data source. Use real for SEC/yfinance S&P 500 data.",
    )
    command_parser.add_argument("--seed", type=int, default=42, help="Random seed for synthetic data.")
    command_parser.add_argument(
        "--limit",
        type=int,
        default=120,
        help="Number of S&P 500 companies to fetch for real data. Use 0 for the full index.",
    )
    command_parser.add_argument("--min-year", type=int, default=2014, help="Earliest fiscal year to keep.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Market opportunity prediction engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Load real, CSV, or synthetic data into SQLite")
    add_data_arguments(ingest_parser)

    train_parser = subparsers.add_parser("train", help="Train and evaluate the opportunity model")
    add_data_arguments(train_parser)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    limit = None if getattr(args, "limit", 120) == 0 else args.limit

    if args.command == "ingest":
        ingest(
            settings=SETTINGS,
            seed=args.seed,
            source=args.source,
            limit=limit,
            min_year=args.min_year,
        )
        print(f"Database ready: {SETTINGS.database_path}")
    elif args.command == "train":
        result = train(
            settings=SETTINGS,
            seed=args.seed,
            source=args.source,
            limit=limit,
            min_year=args.min_year,
        )
        print("Training complete")
        print(result.metrics.to_string(index=False))
        print(f"Predictions: {SETTINGS.predictions_csv}")
        print(f"Model: {SETTINGS.model_path}")


if __name__ == "__main__":
    main()
