from __future__ import annotations

import pandas as pd

from market_opportunity.config import SETTINGS, Settings
from market_opportunity.features import build_features
from market_opportunity.modeling import save_artifacts, train_time_validated_model
from market_opportunity.real_data import fetch_real_sp500_universe
from market_opportunity.storage import load_modeling_frame, save_tables
from market_opportunity.synthetic import make_synthetic_universe


def load_csv_data(settings: Settings = SETTINGS) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings.ensure_directories()
    if not settings.financials_csv.exists() or not settings.prices_csv.exists():
        raise FileNotFoundError("Expected data/raw/financials.csv and data/raw/prices.csv")
    return pd.read_csv(settings.financials_csv), pd.read_csv(settings.prices_csv)


def load_synthetic_data(settings: Settings = SETTINGS, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings.ensure_directories()
    universe = make_synthetic_universe(seed=seed)
    universe.financials.to_csv(settings.raw_dir / "synthetic_financials.csv", index=False)
    universe.prices.to_csv(settings.raw_dir / "synthetic_prices.csv", index=False)
    return universe.financials, universe.prices


def load_real_sp500_data(
    settings: Settings = SETTINGS,
    limit: int | None = 120,
    min_year: int = 2014,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings.ensure_directories()
    universe = fetch_real_sp500_universe(limit=limit, min_year=min_year)
    universe.financials.to_csv(settings.financials_csv, index=False)
    universe.prices.to_csv(settings.prices_csv, index=False)
    return universe.financials, universe.prices


def load_data(
    source: str = "real",
    settings: Settings = SETTINGS,
    seed: int = 42,
    limit: int | None = 120,
    min_year: int = 2014,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if source == "real":
        return load_real_sp500_data(settings=settings, limit=limit, min_year=min_year)
    if source == "csv":
        return load_csv_data(settings=settings)
    if source == "synthetic":
        return load_synthetic_data(settings=settings, seed=seed)
    raise ValueError(f"Unsupported data source: {source}")


def ingest(
    settings: Settings = SETTINGS,
    seed: int = 42,
    source: str = "real",
    limit: int | None = 120,
    min_year: int = 2014,
) -> None:
    financials, prices = load_data(
        source=source,
        settings=settings,
        seed=seed,
        limit=limit,
        min_year=min_year,
    )
    save_tables(settings.database_path, financials, prices)


def train(
    settings: Settings = SETTINGS,
    seed: int = 42,
    source: str = "real",
    limit: int | None = 120,
    min_year: int = 2014,
):
    ingest(settings=settings, seed=seed, source=source, limit=limit, min_year=min_year)
    modeling_frame = load_modeling_frame(settings.database_path)
    features = build_features(modeling_frame)
    features.to_csv(settings.processed_dir / "modeling_frame.csv", index=False)
    result = train_time_validated_model(features, random_state=seed)
    save_artifacts(
        result,
        settings.model_path,
        settings.predictions_csv,
        settings.metrics_csv,
        settings.feature_importance_csv,
    )
    return result
