from __future__ import annotations

import time
from dataclasses import dataclass
from io import StringIO
from typing import Iterable

import pandas as pd
import requests
import yfinance as yf


SP500_WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

DEFAULT_USER_AGENT = (
    "MarketOpportunityEngine/0.1 contact=student-project@example.com "
    "(educational research; no investment advice)"
)

REVENUE_CONCEPTS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
]
EARNINGS_CONCEPTS = ["NetIncomeLoss", "ProfitLoss"]
OPERATING_INCOME_CONCEPTS = ["OperatingIncomeLoss"]
CFO_CONCEPTS = ["NetCashProvidedByUsedInOperatingActivities"]
CAPEX_CONCEPTS = ["PaymentsToAcquirePropertyPlantAndEquipment"]
DEBT_CONCEPTS = [
    "LongTermDebtAndFinanceLeaseObligationsCurrentAndNoncurrent",
    "LongTermDebt",
    "DebtCurrent",
]
EQUITY_CONCEPTS = ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]
ASSET_CONCEPTS = ["Assets"]
CURRENT_ASSET_CONCEPTS = ["AssetsCurrent"]
CURRENT_LIABILITY_CONCEPTS = ["LiabilitiesCurrent"]
RD_CONCEPTS = ["ResearchAndDevelopmentExpense"]
EMPLOYEE_CONCEPTS = ["EntityCommonStockSharesOutstanding"]
SHARES_CONCEPTS = [
    "EntityCommonStockSharesOutstanding",
    "CommonStocksIncludingAdditionalPaidInCapital",
]


@dataclass(frozen=True)
class RealUniverse:
    financials: pd.DataFrame
    prices: pd.DataFrame


def fetch_sp500_constituents(
    limit: int | None = None,
    user_agent: str = DEFAULT_USER_AGENT,
) -> pd.DataFrame:
    response = requests.get(SP500_WIKIPEDIA_URL, headers={"User-Agent": user_agent}, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    constituents = tables[0].rename(
        columns={
            "Symbol": "ticker",
            "Security": "company_name",
            "GICS Sector": "sector",
        }
    )[["ticker", "company_name", "sector"]]
    constituents["ticker"] = constituents["ticker"].str.replace(".", "-", regex=False)
    return constituents.head(limit) if limit else constituents


def fetch_sec_ticker_map(user_agent: str = DEFAULT_USER_AGENT) -> dict[str, int]:
    response = requests.get(SEC_TICKERS_URL, headers={"User-Agent": user_agent}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return {record["ticker"].upper(): int(record["cik_str"]) for record in payload.values()}


def fetch_company_facts(cik: int, user_agent: str = DEFAULT_USER_AGENT) -> dict:
    response = requests.get(
        SEC_COMPANY_FACTS_URL.format(cik=cik),
        headers={"User-Agent": user_agent},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def annual_series(company_facts: dict, concepts: Iterable[str], unit: str = "USD") -> pd.Series:
    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})
    rows: list[dict[str, object]] = []
    for concept in concepts:
        units = us_gaap.get(concept, {}).get("units", {})
        observations = units.get(unit) or next(iter(units.values()), [])
        for observation in observations:
            if observation.get("form") not in {"10-K", "10-K/A", "20-F", "40-F"}:
                continue
            if observation.get("fp") not in {"FY", "CY"}:
                continue
            fy = observation.get("fy")
            value = observation.get("val")
            filed = observation.get("filed", "")
            if fy is None or value is None:
                continue
            rows.append({"fiscal_year": int(fy), "value": float(value), "filed": filed})

    if not rows:
        return pd.Series(dtype="float64")

    frame = pd.DataFrame(rows).sort_values(["fiscal_year", "filed"])
    return frame.groupby("fiscal_year")["value"].last()


def build_financial_rows(company: pd.Series, company_facts: dict) -> pd.DataFrame:
    revenue = annual_series(company_facts, REVENUE_CONCEPTS)
    earnings = annual_series(company_facts, EARNINGS_CONCEPTS)
    operating_income = annual_series(company_facts, OPERATING_INCOME_CONCEPTS)
    cfo = annual_series(company_facts, CFO_CONCEPTS)
    capex = annual_series(company_facts, CAPEX_CONCEPTS)
    debt = annual_series(company_facts, DEBT_CONCEPTS)
    equity = annual_series(company_facts, EQUITY_CONCEPTS)
    assets = annual_series(company_facts, ASSET_CONCEPTS)
    current_assets = annual_series(company_facts, CURRENT_ASSET_CONCEPTS)
    current_liabilities = annual_series(company_facts, CURRENT_LIABILITY_CONCEPTS)
    rd_spending = annual_series(company_facts, RD_CONCEPTS)
    shares = annual_series(company_facts, SHARES_CONCEPTS, unit="shares")

    years = sorted(set(revenue.index) & set(earnings.index) & set(assets.index))
    rows: list[dict[str, object]] = []
    for year in years:
        revenue_value = revenue.get(year, pd.NA)
        earnings_value = earnings.get(year, pd.NA)
        equity_value = equity.get(year, pd.NA)
        assets_value = assets.get(year, pd.NA)
        debt_value = debt.get(year, 0.0)
        free_cash_flow = cfo.get(year, pd.NA)
        if pd.notna(free_cash_flow):
            free_cash_flow = free_cash_flow - abs(capex.get(year, 0.0))

        rows.append(
            {
                "ticker": company["ticker"],
                "company_name": company["company_name"],
                "sector": company["sector"],
                "fiscal_year": year,
                "revenue": revenue_value,
                "earnings": earnings_value,
                "profit_margin": safe_divide(earnings_value, revenue_value),
                "operating_margin": safe_divide(operating_income.get(year, pd.NA), revenue_value),
                "free_cash_flow": free_cash_flow,
                "debt": debt_value,
                "equity": equity_value,
                "assets": assets_value,
                "current_ratio": safe_divide(
                    current_assets.get(year, pd.NA),
                    current_liabilities.get(year, pd.NA),
                ),
                "market_cap": safe_multiply(shares.get(year, pd.NA), pd.NA),
                "pe_ratio": pd.NA,
                "pb_ratio": pd.NA,
                "rd_spending": rd_spending.get(year, 0.0),
                "employee_growth": 0.0,
            }
        )

    return pd.DataFrame(rows)


def fetch_price_history(tickers: list[str], start_year: int, end_year: int) -> pd.DataFrame:
    download_tickers = tickers + ["^GSPC"]
    prices = yf.download(
        download_tickers,
        start=f"{start_year}-01-01",
        end=f"{end_year + 2}-01-15",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    close = prices["Close"] if isinstance(prices.columns, pd.MultiIndex) else prices[["Close"]]
    if "^GSPC" not in close.columns:
        raise ValueError("Could not fetch S&P 500 benchmark prices from yfinance.")
    return close.dropna(how="all")


def enrich_with_market_data(financials: pd.DataFrame, close_prices: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    enriched = financials.copy()

    for index, record in enriched.iterrows():
        ticker = record["ticker"]
        year = int(record["fiscal_year"])
        if ticker not in close_prices.columns:
            continue
        stock_start = year_end_close(close_prices[ticker], year)
        stock_end = year_end_close(close_prices[ticker], year + 1)
        sp_start = year_end_close(close_prices["^GSPC"], year)
        sp_end = year_end_close(close_prices["^GSPC"], year + 1)
        if any(pd.isna(value) for value in [stock_start, stock_end, sp_start, sp_end]):
            continue

        stock_return = stock_end / stock_start - 1
        sp_return = sp_end / sp_start - 1
        market_cap = record["market_cap"]
        if pd.isna(market_cap):
            market_cap = abs(record["revenue"]) * 2.0

        enriched.loc[index, "market_cap"] = market_cap
        enriched.loc[index, "pe_ratio"] = safe_divide(market_cap, abs(record["earnings"]))
        enriched.loc[index, "pb_ratio"] = safe_divide(market_cap, record["equity"])

        rows.append(
            {
                "ticker": ticker,
                "fiscal_year": year,
                "sp500_return_next_12m": sp_return,
                "stock_return_next_12m": stock_return,
                "close_price_year_end": stock_start,
            }
        )

    prices = pd.DataFrame(rows)
    valid_keys = set(zip(prices["ticker"], prices["fiscal_year"], strict=False)) if not prices.empty else set()
    enriched = enriched[
        enriched.apply(lambda row: (row["ticker"], row["fiscal_year"]) in valid_keys, axis=1)
    ]
    return enriched.reset_index(drop=True), prices.reset_index(drop=True)


def year_end_close(series: pd.Series, year: int) -> float:
    year_values = series.loc[(series.index.year == year) & (series.index.month == 12) & series.notna()]
    if year_values.empty:
        return float("nan")
    return float(year_values.iloc[-1])


def fetch_real_sp500_universe(
    limit: int | None = 120,
    min_year: int = 2014,
    user_agent: str = DEFAULT_USER_AGENT,
    sec_sleep_seconds: float = 0.12,
) -> RealUniverse:
    constituents = fetch_sp500_constituents(limit=limit, user_agent=user_agent)
    ticker_map = fetch_sec_ticker_map(user_agent=user_agent)
    financial_frames: list[pd.DataFrame] = []

    for _, company in constituents.iterrows():
        cik = ticker_map.get(company["ticker"].replace("-", ".").upper()) or ticker_map.get(
            company["ticker"].upper()
        )
        if cik is None:
            continue
        try:
            facts = fetch_company_facts(cik, user_agent=user_agent)
            frame = build_financial_rows(company, facts)
            if not frame.empty:
                frame = frame[frame["fiscal_year"] >= min_year]
                financial_frames.append(frame)
        except requests.RequestException:
            continue
        time.sleep(sec_sleep_seconds)

    if not financial_frames:
        raise ValueError("No SEC fundamentals were fetched. Check network access or SEC availability.")

    financials = pd.concat(financial_frames, ignore_index=True)
    tickers = sorted(financials["ticker"].unique().tolist())
    close_prices = fetch_price_history(
        tickers,
        start_year=int(financials["fiscal_year"].min()),
        end_year=int(financials["fiscal_year"].max()),
    )
    financials, prices = enrich_with_market_data(financials, close_prices)
    financials = clean_real_financials(financials)
    return RealUniverse(financials=financials, prices=prices)


def clean_real_financials(financials: pd.DataFrame) -> pd.DataFrame:
    data = financials.copy()
    numeric_columns = [
        "revenue",
        "earnings",
        "profit_margin",
        "operating_margin",
        "free_cash_flow",
        "debt",
        "equity",
        "assets",
        "current_ratio",
        "market_cap",
        "pe_ratio",
        "pb_ratio",
        "rd_spending",
        "employee_growth",
    ]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    data["free_cash_flow"] = data["free_cash_flow"].fillna(data["earnings"])
    data["operating_margin"] = data["operating_margin"].fillna(data["profit_margin"])
    data["current_ratio"] = data["current_ratio"].fillna(1.0)
    data["rd_spending"] = data["rd_spending"].fillna(0.0)
    data["employee_growth"] = data["employee_growth"].fillna(0.0)
    data = data.dropna(subset=["revenue", "earnings", "equity", "assets", "market_cap", "pe_ratio", "pb_ratio"])
    return data


def safe_divide(numerator, denominator) -> float | pd.NA:
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return pd.NA
    return float(numerator) / float(denominator)


def safe_multiply(left, right) -> float | pd.NA:
    if pd.isna(left) or pd.isna(right):
        return pd.NA
    return float(left) * float(right)
