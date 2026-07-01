from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SECTORS = [
    "Technology",
    "Healthcare",
    "Financials",
    "Industrials",
    "Consumer",
    "Energy",
    "Utilities",
    "Materials",
]


@dataclass(frozen=True)
class SyntheticUniverse:
    financials: pd.DataFrame
    prices: pd.DataFrame


def make_synthetic_universe(
    company_count: int = 120,
    start_year: int = 2014,
    end_year: int = 2025,
    seed: int = 42,
) -> SyntheticUniverse:
    """Create a realistic demo dataset when no paid financial data source is configured."""

    rng = np.random.default_rng(seed)
    tickers = [f"C{i:03d}" for i in range(1, company_count + 1)]
    years = list(range(start_year, end_year + 1))

    company_quality = rng.normal(0.0, 1.0, company_count)
    company_size = rng.lognormal(mean=9.2, sigma=0.9, size=company_count)
    sector_by_ticker = {ticker: rng.choice(SECTORS) for ticker in tickers}

    financial_rows: list[dict[str, object]] = []
    price_rows: list[dict[str, object]] = []

    sp500_return_by_year = {
        year: rng.normal(0.085, 0.16) + 0.02 * np.sin((year - start_year) / 2)
        for year in years
    }

    for idx, ticker in enumerate(tickers):
        revenue = company_size[idx] * rng.uniform(0.7, 1.4)
        debt_ratio_anchor = np.clip(rng.normal(0.55, 0.22), 0.05, 1.4)
        price = rng.uniform(18, 180)

        for year in years:
            macro = sp500_return_by_year[year]
            quality = company_quality[idx]
            growth = rng.normal(0.08 + 0.025 * quality + 0.12 * macro, 0.09)
            revenue *= max(0.65, 1 + growth)
            profit_margin = np.clip(rng.normal(0.09 + 0.025 * quality, 0.06), -0.15, 0.34)
            operating_margin = np.clip(profit_margin + rng.normal(0.025, 0.025), -0.12, 0.42)
            earnings = revenue * profit_margin
            free_cash_flow = earnings * rng.normal(0.8, 0.22)
            assets = revenue * rng.uniform(0.7, 2.0)
            debt = assets * max(0.02, debt_ratio_anchor + rng.normal(0, 0.08))
            equity = max(assets - debt, assets * 0.08)
            market_cap = revenue * rng.uniform(1.3, 7.5) * max(0.35, 1 + quality / 5)
            pe_ratio = np.clip(market_cap / max(abs(earnings), revenue * 0.01), 4, 95)
            pb_ratio = np.clip(market_cap / max(equity, 1), 0.2, 18)
            employee_growth = rng.normal(0.045 + growth * 0.35, 0.08)
            rd_spending = revenue * rng.uniform(0.0, 0.18)

            expected_alpha = (
                0.28 * growth
                + 0.36 * profit_margin
                + 0.18 * free_cash_flow / max(revenue, 1)
                - 0.06 * debt / max(equity, 1)
                - 0.0018 * pe_ratio
                + 0.035 * quality
            )
            one_year_return = macro + expected_alpha + rng.normal(0, 0.16)
            price *= max(0.2, 1 + one_year_return)

            financial_rows.append(
                {
                    "ticker": ticker,
                    "company_name": f"Company {idx + 1:03d}",
                    "sector": sector_by_ticker[ticker],
                    "fiscal_year": year,
                    "revenue": revenue,
                    "earnings": earnings,
                    "profit_margin": profit_margin,
                    "operating_margin": operating_margin,
                    "free_cash_flow": free_cash_flow,
                    "debt": debt,
                    "equity": equity,
                    "assets": assets,
                    "current_ratio": np.clip(rng.normal(1.7 + 0.15 * quality, 0.45), 0.35, 4.5),
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "rd_spending": rd_spending,
                    "employee_growth": employee_growth,
                }
            )
            price_rows.append(
                {
                    "ticker": ticker,
                    "fiscal_year": year,
                    "sp500_return_next_12m": macro,
                    "stock_return_next_12m": one_year_return,
                    "close_price_year_end": price,
                }
            )

    return SyntheticUniverse(pd.DataFrame(financial_rows), pd.DataFrame(price_rows))
