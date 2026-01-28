#!/usr/bin/env python3
"""Fetch real stock price data using yfinance for use in practice questions.

Downloads OHLCV data for given tickers and saves as CSV or returns as JSON.
This data can be embedded into notebook setup cells to give students real
market data to work with.

Usage:
    # Fetch and save as CSV
    python fetch_price_data.py --tickers AAPL MSFT TSLA --period 1y --output /tmp/prices.csv

    # Fetch and print as JSON (for piping into notebooks)
    python fetch_price_data.py --tickers AAPL MSFT --period 6mo --format json

    # Fetch with specific date range
    python fetch_price_data.py --tickers SPY QQQ --start 2023-01-01 --end 2024-01-01

    # Fetch and output a Python code snippet that creates the DataFrame
    python fetch_price_data.py --tickers AAPL MSFT --period 3mo --format code

    # Random tickers (requires random_tickers.py)
    python fetch_price_data.py --random 4 --period 6mo --format code

Requires: yfinance, pandas
"""

import argparse
import json
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import yfinance as yf


def fetch_prices(tickers, period=None, start=None, end=None, column="Close"):
    """Fetch price data for the given tickers.

    Returns a DataFrame with dates as index and tickers as columns.
    """
    if start and end:
        data = yf.download(tickers, start=start, end=end, progress=False)
    else:
        data = yf.download(tickers, period=period or "6mo", progress=False)

    if data.empty:
        print(f"No data returned for {tickers}", file=sys.stderr)
        sys.exit(1)

    # yfinance returns MultiIndex columns for multiple tickers
    if isinstance(data.columns, pd.MultiIndex):
        prices = data[column]
    else:
        prices = data[[column]]
        prices.columns = tickers if isinstance(tickers, list) else [tickers]

    prices.index = prices.index.strftime("%Y-%m-%d")
    prices.index.name = "Date"
    return prices


def to_code_snippet(df, variable_name="prices"):
    """Convert a DataFrame to a Python code string that recreates it."""
    lines = []
    lines.append("import pandas as pd")
    lines.append("")

    # Output as a dict of lists for compactness
    lines.append(f"# Real market data fetched from Yahoo Finance")
    lines.append(f"{variable_name} = pd.DataFrame({{")
    for col in df.columns:
        values = df[col].round(2).tolist()
        lines.append(f"    '{col}': {values},")
    lines.append(f"}}, index=pd.DatetimeIndex({list(df.index)}))")
    lines.append(f"{variable_name}.index.name = 'Date'")

    return "\n".join(lines)


def to_returns_code(df, variable_name="returns"):
    """Convert price DataFrame to a returns code snippet."""
    returns = df.pct_change().dropna()
    lines = []
    lines.append("import pandas as pd")
    lines.append("import numpy as np")
    lines.append("")
    lines.append(f"# Daily returns computed from real market data")
    lines.append(f"{variable_name} = pd.DataFrame({{")
    for col in returns.columns:
        values = [round(v, 6) for v in returns[col].tolist()]
        lines.append(f"    '{col}': {values},")
    lines.append(f"}}, index=pd.DatetimeIndex({list(returns.index)}))")
    lines.append(f"{variable_name}.index.name = 'Date'")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch stock price data for practice notebooks.")
    parser.add_argument("--tickers", nargs="+", help="Ticker symbols (e.g. AAPL MSFT TSLA).")
    parser.add_argument("--random", type=int, default=0, help="Pick N random tickers instead of specifying them.")
    parser.add_argument("--sector", type=str, default="", help="Sector for random tickers.")
    parser.add_argument("--period", type=str, default="6mo", help="Data period: 1mo, 3mo, 6mo, 1y, 2y (default: 6mo).")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD). Overrides --period.")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD). Overrides --period.")
    parser.add_argument("--column", type=str, default="Close", help="Price column: Open, High, Low, Close, Volume (default: Close).")
    parser.add_argument("--format", type=str, default="csv", choices=["csv", "json", "code", "returns"], help="Output format.")
    parser.add_argument("--output", type=str, help="Output file path. If omitted, prints to stdout.")
    args = parser.parse_args()

    # Resolve tickers
    if args.random > 0:
        from random_tickers import pick_tickers
        tickers = pick_tickers(args.random, sector=args.sector or None)
        print(f"Selected tickers: {tickers}", file=sys.stderr)
    elif args.tickers:
        tickers = args.tickers
    else:
        print("Provide --tickers or --random.", file=sys.stderr)
        sys.exit(1)

    # Fetch data
    df = fetch_prices(
        tickers,
        period=args.period,
        start=args.start,
        end=args.end,
        column=args.column,
    )

    # Format output
    if args.format == "csv":
        output = df.to_csv()
    elif args.format == "json":
        output = df.to_json(orient="columns", indent=2)
    elif args.format == "code":
        output = to_code_snippet(df)
    elif args.format == "returns":
        output = to_returns_code(df)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
