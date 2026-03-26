---
name: quant-connect
description: Build, refactor, and explain QuantConnect LEAN algorithms in Python using QCAlgorithm, including data subscriptions, event handlers, scheduling, history, indicators, and order placement. Use when translating strategy logic into QuantConnect's Python API, debugging backtests/live behavior, or implementing core algorithm patterns.
---

# QuantConnect Python Algorithms

## Overview
Enable fast, correct construction of QuantConnect LEAN algorithms in Python. Focus on core QCAlgorithm lifecycle, data access, scheduling, indicators, history, and orders (not exhaustive API coverage).

## Workflow
1. Clarify the strategy, asset class, resolution, and backtest vs live assumptions.
2. Draft the algorithm skeleton with `initialize` and `on_data`; store `Symbol` objects from `add_*` calls.
3. Add indicators and warm-up, plus any scheduled callbacks.
4. Implement trade logic and order placement.
5. Validate data availability, market hours, and event timing.

## Core Patterns (Python)
- Define a single class inheriting `QCAlgorithm`. Use `initialize` for setup and `on_data(self, slice)` as the primary data event handler.
- Use `add_equity` (or other `add_*`) in `initialize` and store the returned `Symbol` for later `Slice` access.
- Use indicator helpers like `self.sma(symbol, period, resolution)` for auto-updating indicators; use `self.set_warm_up` or `self.warm_up_indicator` so indicators are ready before trading.
- Use `self.history(...)` in `initialize` or runtime to fetch recent data for features and checks.

### Minimal Skeleton
```python
from AlgorithmImports import *

class MyAlgo(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2023, 1, 1)
        self.set_cash(100000)
        self.symbol = self.add_equity("SPY", Resolution.MINUTE).symbol
        self.sma = self.sma(self.symbol, 20, Resolution.DAILY)
        self.set_warm_up(20, Resolution.DAILY)

    def on_data(self, slice: Slice):
        if self.is_warming_up:
            return
        if not slice.contains_key(self.symbol):
            return
        if self.sma.is_ready and not self.portfolio.invested:
            self.market_order(self.symbol, 10)
```

## Scheduling
- Use `self.schedule.on(date_rules..., time_rules..., callback)` for timed logic.
- Account for the fact that in backtests, scheduled events run on the next data slice; in live, they run at the scheduled clock time.

## Data Access
- Use `slice.contains_key(symbol)` before accessing per-symbol data.
- Access trade bars via `slice.bars[symbol]` and quote bars via `slice.quote_bars[symbol]` when present.

## Orders
- Use `self.market_order(symbol, quantity)` for immediate execution and `self.limit_order(symbol, quantity, limit_price)` for price-constrained orders.

## References
- Read `references/quantconnect-python-core.md` for quick patterns, doc links, and API nuances.
