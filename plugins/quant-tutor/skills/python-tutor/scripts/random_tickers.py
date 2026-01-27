#!/usr/bin/env python3
"""Pick random ticker sets for use in practice questions.

Provides curated lists of tickers organized by sector and market cap,
plus functions to randomly select diverse sets.

Usage:
    # CLI: print a random set of tickers as JSON
    python random_tickers.py --count 4
    python random_tickers.py --count 3 --sector tech
    python random_tickers.py --count 5 --diverse   # one per sector

    # As a module:
    from random_tickers import pick_tickers, pick_diverse, TICKER_POOLS
    tickers = pick_tickers(4)
    tickers = pick_tickers(3, sector='tech')
    tickers = pick_diverse(5)
"""

import argparse
import json
import random

TICKER_POOLS = {
    "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSM", "AVGO", "ORCL", "CRM", "ADBE", "INTC", "AMD", "QCOM", "CSCO"],
    "financials": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW", "AXP", "USB"],
    "consumer": ["LULU", "NKE", "SBUX", "MCD", "TGT", "WMT", "COST", "HD", "LOW", "TJX"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL"],
    "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "BMY", "AMGN"],
    "etfs": ["SPY", "QQQ", "IWM", "DIA", "TLT", "GLD", "VXX", "XLF", "XLE", "XLK"],
    "crypto_related": ["COIN", "MSTR", "MARA", "RIOT", "SQ"],
}

ALL_TICKERS = [t for pool in TICKER_POOLS.values() for t in pool]


def pick_tickers(count=4, sector=None):
    """Pick random tickers, optionally from a specific sector."""
    pool = TICKER_POOLS.get(sector, ALL_TICKERS) if sector else ALL_TICKERS
    count = min(count, len(pool))
    return random.sample(pool, count)


def pick_diverse(count=5):
    """Pick tickers from different sectors for variety."""
    sectors = list(TICKER_POOLS.keys())
    random.shuffle(sectors)
    result = []
    for sector in sectors:
        if len(result) >= count:
            break
        result.append(random.choice(TICKER_POOLS[sector]))
    return result[:count]


def main():
    parser = argparse.ArgumentParser(description="Pick random ticker sets.")
    parser.add_argument("--count", type=int, default=4, help="Number of tickers (default: 4).")
    parser.add_argument("--sector", type=str, default="", help=f"Sector: {', '.join(TICKER_POOLS.keys())}.")
    parser.add_argument("--diverse", action="store_true", help="Pick one ticker per sector for diversity.")
    parser.add_argument("--list-sectors", action="store_true", help="List available sectors and exit.")
    args = parser.parse_args()

    if args.list_sectors:
        for sector, tickers in TICKER_POOLS.items():
            print(f"{sector}: {', '.join(tickers)}")
        return

    if args.diverse:
        tickers = pick_diverse(args.count)
    else:
        tickers = pick_tickers(args.count, sector=args.sector or None)

    print(json.dumps(tickers))


if __name__ == "__main__":
    main()
