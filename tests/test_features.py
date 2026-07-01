import pandas as pd
import pytest

from market_opportunity.features import TARGET_COLUMN, build_features


def test_build_features_creates_target_and_growth_fields():
    frame = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "company_name": "AAA Inc",
                "sector": "Technology",
                "fiscal_year": 2023,
                "revenue": 100,
                "earnings": 10,
                "profit_margin": 0.10,
                "operating_margin": 0.12,
                "free_cash_flow": 8,
                "debt": 20,
                "equity": 50,
                "assets": 80,
                "current_ratio": 1.8,
                "market_cap": 500,
                "pe_ratio": 20,
                "pb_ratio": 4,
                "rd_spending": 5,
                "employee_growth": 0.02,
                "sp500_return_next_12m": 0.10,
                "stock_return_next_12m": 0.12,
                "close_price_year_end": 50,
            },
            {
                "ticker": "AAA",
                "company_name": "AAA Inc",
                "sector": "Technology",
                "fiscal_year": 2024,
                "revenue": 120,
                "earnings": 14,
                "profit_margin": 0.116,
                "operating_margin": 0.14,
                "free_cash_flow": 11,
                "debt": 19,
                "equity": 60,
                "assets": 85,
                "current_ratio": 2.0,
                "market_cap": 620,
                "pe_ratio": 22,
                "pb_ratio": 4.2,
                "rd_spending": 6,
                "employee_growth": 0.04,
                "sp500_return_next_12m": 0.08,
                "stock_return_next_12m": 0.15,
                "close_price_year_end": 62,
            },
        ]
    )

    features = build_features(frame)

    assert len(features) == 1
    assert features.loc[0, "revenue_growth"] == pytest.approx(0.2)
    assert features.loc[0, TARGET_COLUMN] == 1
