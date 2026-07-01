from __future__ import annotations

import pandas as pd


def top_drivers(feature_importance: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    """Return the most influential model features for dashboard display."""

    columns = ["feature", "importance"]
    return feature_importance[columns].sort_values("importance", ascending=False).head(limit)
