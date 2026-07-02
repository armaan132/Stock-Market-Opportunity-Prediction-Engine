import pandas as pd

from market_opportunity.modeling import backtest_top_ranked_portfolio


def test_backtest_top_ranked_portfolio_compares_against_sp500():
    holdout = pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "fiscal_year": 2022,
                "opportunity_probability": 0.9,
                "stock_return_next_12m": 0.20,
                "sp500_return_next_12m": 0.10,
            },
            {
                "ticker": "BBB",
                "fiscal_year": 2022,
                "opportunity_probability": 0.8,
                "stock_return_next_12m": 0.00,
                "sp500_return_next_12m": 0.10,
            },
            {
                "ticker": "CCC",
                "fiscal_year": 2022,
                "opportunity_probability": 0.1,
                "stock_return_next_12m": 0.50,
                "sp500_return_next_12m": 0.10,
            },
        ]
    )

    result = backtest_top_ranked_portfolio(holdout, top_n=2)

    assert result.loc[0, "portfolio_return"] == 0.10
    assert result.loc[0, "sp500_return"] == 0.10
    assert result.loc[0, "excess_return"] == 0.0
    assert result.loc[1, "fiscal_year"] == "all_holdout_years"
