CREATE TABLE IF NOT EXISTS financials (
    ticker TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    revenue REAL NOT NULL,
    earnings REAL NOT NULL,
    profit_margin REAL NOT NULL,
    operating_margin REAL NOT NULL,
    free_cash_flow REAL NOT NULL,
    debt REAL NOT NULL,
    equity REAL NOT NULL,
    assets REAL NOT NULL,
    current_ratio REAL NOT NULL,
    market_cap REAL NOT NULL,
    pe_ratio REAL NOT NULL,
    pb_ratio REAL NOT NULL,
    rd_spending REAL NOT NULL,
    employee_growth REAL NOT NULL,
    PRIMARY KEY (ticker, fiscal_year)
);

CREATE TABLE IF NOT EXISTS market_returns (
    ticker TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    sp500_return_next_12m REAL NOT NULL,
    stock_return_next_12m REAL NOT NULL,
    close_price_year_end REAL NOT NULL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker, fiscal_year) REFERENCES financials(ticker, fiscal_year)
);
