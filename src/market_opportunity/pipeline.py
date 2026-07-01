from __future__ import annotations

import pandas as pd

from market_opportunity.config import SETTINGS, Settings
from market_opportunity.features import build_features
from market_opportunity.modeling import save_artifacts, train_time_validated_model
from market_opportunity.storage import load_modeling_frame, save_tables
from market_opportunity.synthetic import make_synthetic_universe


def load_or_generate_data(settings: Settings = SETTINGS, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings.ensure_directories()
    if settings.financials_csv.exists() and settings.prices_csv.exists():
        return pd.read_csv(settings.financials_csv), pd.read_csv(settings.prices_csv)

    universe = make_synthetic_universe(seed=seed)
    universe.financials.to_csv(settings.financials_csv, index=False)
    universe.prices.to_csv(settings.prices_csv, index=False)
    return universe.financials, universe.prices


def ingest(settings: Settings = SETTINGS, seed: int = 42) -> None:
    financials, prices = load_or_generate_data(settings=settings, seed=seed)
    save_tables(settings.database_path, financials, prices)


def train(settings: Settings = SETTINGS, seed: int = 42):
    ingest(settings=settings, seed=seed)
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
