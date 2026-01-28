# Quant Tutor

A Claude Code plugin for quantitative finance tutoring and Python practice problem generation.

## Overview

This plugin generates Jupyter notebook practice challenges for Python programming concepts relevant to quantitative finance. It creates varied, real-world problems using actual market data and randomized scenarios to ensure each practice session is unique.

## What's Included

### Commands (2)

Slash commands for quick access to practice generation:

- `/practice-pandas` - Generate pandas practice problems (DataFrames, time series, groupby, etc.)
- `/practice-algorithms` - Generate algorithm practice problems (sorting, searching, recursion, etc.)

### Skills (1)

Claude uses this specialized capability to generate practice materials:

- **python-practice** - Generate pandas and algorithms practice notebooks with real market data, hidden hints, and solutions

### Hooks (1)

Automated tasks that run during skill execution:

- **capture-skill-output** - Captures Bash command output after tool use for logging and debugging

## Quick Start

### 1. Generate Pandas Practice

Use the command:

```
/practice-pandas
```

or describe what you want:

```
Generate 10 medium difficulty pandas practice problems
```

Claude will ask about subcategory, difficulty, count, and output location, then generate a notebook with real stock data.

### 2. Generate Algorithm Practice

Use the command:

```
/practice-algorithms
```

or describe what you want:

```
Give me 5 hard algorithm challenges focusing on sorting and recursion
```

### 3. Customize Your Practice

Be specific about what you want:

```
Create pandas time series problems using tech stocks from the last 6 months
```

```
I want to practice binary search and divide-and-conquer algorithms
```

### 4. Avoid Repeating Problems

If you have previous notebooks:

```
Generate new pandas problems, but check ~/notebooks/previous for exercises I've already done
```

The skill will scan your previous notebooks and vary the data/scenarios to keep challenges fresh.

## What You Get

Each generated notebook includes:

- **Title cell** with category, difficulty, date, and question count
- **Setup cell** with imports and real market data (for pandas) or test helpers (for algorithms)
- **Challenge cells** with clear problem statements and expected output
- **Hidden hints** wrapped in `<details>` tags (easy/medium only)
- **Empty code cells** for your solutions
- **Hidden solutions** you can reveal when ready

## Categories and Topics

### Pandas

- **Series** - creation, retrieval, modification, alignment, built-in methods
- **DataFrames** - loc/iloc, slicing, boolean masks, column operations
- **Data exploration** - apply/applymap, correlations, covariance
- **Missing data** - detection, dropping, filling, interpolation
- **Reindexing and sorting** - reindex, drop, sort_index, sort_values
- **Categorical data** - unique values, value_counts, isin, dummy variables
- **File I/O** - reading/writing CSV, Excel, pickle
- **Multi-indexing** - multi-index DataFrames, stack/unstack, swaplevel
- **Time series** - timestamps, offsets, date ranges, resampling, shifting
- **GroupBy, pivot, merge** - groupby, pivot_table, merge/join, concat
- **Rolling and quantiles** - rolling windows, qcut, shift for returns
- **Plotting** - line, bar, scatter, histograms, heatmaps

### Algorithms

- **Data structures** - lists, dicts, sets, tuples, deques, heaps
- **Sorting** - bubble, merge, quick, insertion sort
- **Searching** - linear search, binary search
- **Recursion** - factorial, fibonacci, tree traversal, divide and conquer
- **String manipulation** - reversal, palindromes, anagrams, pattern matching
- **Math and logic** - primes, GCD, modular arithmetic, bit manipulation

## Difficulty Levels

| Level | Description | Hints | Expected Code |
|-------|-------------|-------|---------------|
| Easy | Single concept | Yes (hidden) | 1-5 lines |
| Medium | 2-3 concepts combined | Yes (hidden) | 5-15 lines |
| Hard | Multi-step, chained operations | No | 10-30+ lines |

## Plugin Structure

```
quant-tutor/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/
│   ├── practice-pandas.md       # /practice-pandas command
│   └── practice-algorithms.md   # /practice-algorithms command
├── skills/
│   └── python-practice/         # Main practice generator
│       ├── SKILL.md             # Skill instructions
│       ├── scripts/             # Helper scripts
│       │   ├── generate_notebook.py
│       │   ├── random_tickers.py
│       │   ├── fetch_price_data.py
│       │   └── random_data.py
│       ├── templates/           # Notebook templates
│       │   ├── pandas_template.ipynb
│       │   └── algorithms_template.ipynb
│       ├── questions/           # Pre-written question bank
│       │   └── bank.json
│       ├── references/          # Topic documentation
│       │   ├── PANDAS_NOTE.md
│       │   ├── PANDAS_FOR_DATA_SCIENCE.md
│       │   ├── NUMPY.md
│       │   ├── ALGORITHMS.md
│       │   └── PYTHON_NOTES.md
│       └── examples/
│           └── PANDAS_EXAMPLES.md
├── hooks/
│   ├── hooks.json
│   └── capture-skill-output.sh
└── README.md
```

## How It Works

### Notebook Generation Flow

When you use `/practice-pandas` or `/practice-algorithms`:

1. **Parameter gathering** - Claude asks about subcategory, difficulty, count, and output location
2. **Previous exercise check** - If folder provided, scans for already-used prompts
3. **Data generation** - Scripts fetch real market data and generate random values
4. **Notebook building** - `generate_notebook.py` assembles the `.ipynb` file
5. **Delivery** - Notebook saved to specified location

### Example Flow

```
User: /practice-pandas

Claude → python-practice skill
  → Asks: subcategory? difficulty? count? output folder? previous exercises?
  → Runs random_tickers.py (picks fresh tickers)
  → Runs fetch_price_data.py (gets real OHLCV data)
  → Filters question bank for selected subcategory
  → Builds notebook with:
    - Title cell with metadata
    - Setup cell with real market data
    - Challenge cells with hidden hints
    - Empty solution cells
    - Hidden answer cells
  → Saves notebook
  → Reports path to user
```

## Scripts Reference

### `generate_notebook.py`
Builds `.ipynb` files from templates and question data.

```bash
# From question bank
python scripts/generate_notebook.py --bank questions/bank.json \
  --category pandas --difficulty easy --count 5 --output .

# From custom questions
python scripts/generate_notebook.py --questions /tmp/my_questions.json \
  --category algorithms --output .
```

### `random_tickers.py`
Picks random stock symbols for varied practice data.

```bash
python scripts/random_tickers.py --count 4
python scripts/random_tickers.py --count 3 --sector tech
python scripts/random_tickers.py --count 5 --diverse
```

### `fetch_price_data.py`
Fetches real market data from Yahoo Finance.

```bash
python scripts/fetch_price_data.py --tickers AAPL MSFT --period 6mo --format code
python scripts/fetch_price_data.py --random 4 --period 1y --format returns
```

### `random_data.py`
Generates random numbers, dates, and messy DataFrames.

```bash
python scripts/random_data.py --type integers --count 10 --min 1 --max 100
python scripts/random_data.py --type messy_dataframe --rows 20
```

## Tips

- **Use commands** - `/practice-pandas` and `/practice-algorithms` are the fastest way to start
- **Be specific** - Tell Claude exactly what topics you want to practice
- **Use previous exercises folder** - Prevents repeating the same problems
- **Start with easy** - Build confidence before tackling hard challenges
- **Real data matters** - Market data makes problems more engaging and realistic
- **Hidden hints help** - Use them when stuck, but try without first

## Resources

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [yfinance](https://github.com/ranaroussi/yfinance) - Market data API
