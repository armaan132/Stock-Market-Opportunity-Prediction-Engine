from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Central file locations for the local platform."""

    raw_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_dir: Path = PROJECT_ROOT / "data" / "processed"
    external_dir: Path = PROJECT_ROOT / "data" / "external"
    model_dir: Path = PROJECT_ROOT / "models"
    database_path: Path = PROJECT_ROOT / "data" / "processed" / "market_opportunity.sqlite"
    financials_csv: Path = PROJECT_ROOT / "data" / "raw" / "financials.csv"
    prices_csv: Path = PROJECT_ROOT / "data" / "raw" / "prices.csv"
    predictions_csv: Path = PROJECT_ROOT / "data" / "processed" / "latest_predictions.csv"
    metrics_csv: Path = PROJECT_ROOT / "data" / "processed" / "model_metrics.csv"
    backtest_csv: Path = PROJECT_ROOT / "data" / "processed" / "backtest_results.csv"
    feature_importance_csv: Path = PROJECT_ROOT / "data" / "processed" / "feature_importance.csv"
    model_path: Path = PROJECT_ROOT / "models" / "opportunity_model.joblib"

    def ensure_directories(self) -> None:
        for path in [self.raw_dir, self.processed_dir, self.external_dir, self.model_dir]:
            path.mkdir(parents=True, exist_ok=True)


SETTINGS = Settings()
