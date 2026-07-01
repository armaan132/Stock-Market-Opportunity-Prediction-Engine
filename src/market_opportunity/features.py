from __future__ import annotations

import pandas as pd
import numpy as np


NUMERIC_FEATURES = [
    "revenue_growth",
    "earnings_growth",
    "profit_margin",
    "operating_margin",
    "free_cash_flow_margin",
    "debt_to_equity",
    "current_ratio",
    "return_on_equity",
    "return_on_assets",
    "pe_ratio",
    "pb_ratio",
    "log_market_cap",
    "rd_to_revenue",
    "employee_growth",
]

CATEGORICAL_FEATURES = ["sector"]
TARGET_COLUMN = "outperformed_sp500"


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.sort_values(["ticker", "fiscal_year"]).copy()

    data["revenue_growth"] = data.groupby("ticker")["revenue"].pct_change()
    data["earnings_growth"] = data.groupby("ticker")["earnings"].pct_change()
    data["free_cash_flow_margin"] = data["free_cash_flow"] / data["revenue"].replace(0, pd.NA)
    data["debt_to_equity"] = data["debt"] / data["equity"].replace(0, pd.NA)
    data["return_on_equity"] = data["earnings"] / data["equity"].replace(0, pd.NA)
    data["return_on_assets"] = data["earnings"] / data["assets"].replace(0, pd.NA)
    data["log_market_cap"] = np.log(data["market_cap"].clip(lower=1))
    data["rd_to_revenue"] = data["rd_spending"] / data["revenue"].replace(0, pd.NA)
    data[TARGET_COLUMN] = (data["stock_return_next_12m"] > data["sp500_return_next_12m"]).astype(int)
    data["excess_return_next_12m"] = data["stock_return_next_12m"] - data["sp500_return_next_12m"]

    data[NUMERIC_FEATURES] = data[NUMERIC_FEATURES].replace([float("inf"), float("-inf")], pd.NA)
    data = data.dropna(subset=NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN])
    return data.reset_index(drop=True)


def feature_columns() -> list[str]:
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES
