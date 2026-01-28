#!/usr/bin/env python3
"""Generate random data for practice questions.

Provides random numbers, ranges, sample DataFrames, and other data generators
to keep practice questions varied and non-repeating.

Usage:
    # CLI: generate random data as JSON
    python random_data.py --type integers --count 10 --min 1 --max 100
    python random_data.py --type floats --count 5 --min -0.05 --max 0.05 --decimals 4
    python random_data.py --type date_range --start 2020-01-01 --periods 30 --freq B
    python random_data.py --type names --count 8
    python random_data.py --type messy_dataframe --rows 20

    # As a module:
    from random_data import random_integers, random_floats, random_names, messy_dataframe
"""

import argparse
import json
import random
import string
from datetime import datetime, timedelta


# Name pools for generating fake employee/person data
FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank",
    "Ivy", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zach",
]

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations", "Research", "Support"]
CITIES = ["New York", "San Francisco", "Chicago", "Austin", "Seattle", "Boston", "Denver", "Portland"]
PRODUCTS = ["Widget A", "Widget B", "Gadget X", "Gadget Y", "Tool Alpha", "Tool Beta", "Service Pro", "Service Basic"]


def random_integers(count=10, min_val=1, max_val=100):
    """Generate a list of random integers."""
    return [random.randint(min_val, max_val) for _ in range(count)]


def random_floats(count=10, min_val=-0.05, max_val=0.05, decimals=4):
    """Generate a list of random floats."""
    return [round(random.uniform(min_val, max_val), decimals) for _ in range(count)]


def random_date_range(start="2020-01-01", periods=30, freq="D"):
    """Generate a list of date strings.

    freq: D=daily, B=business days, W=weekly, M=monthly (approximate)
    """
    dt = datetime.strptime(start, "%Y-%m-%d")
    dates = []
    freq_days = {"D": 1, "B": 1, "W": 7, "M": 30}
    step = freq_days.get(freq, 1)

    for _ in range(periods):
        dates.append(dt.strftime("%Y-%m-%d"))
        dt += timedelta(days=step)
        if freq == "B":
            while dt.weekday() >= 5:
                dt += timedelta(days=1)

    return dates


def random_names(count=8):
    """Pick random unique names."""
    count = min(count, len(FIRST_NAMES))
    return random.sample(FIRST_NAMES, count)


def random_series_data(count=5, index_type="tickers"):
    """Generate data suitable for creating a pandas Series.

    Returns a dict with keys and numeric values.
    """
    from random_tickers import pick_tickers

    if index_type == "tickers":
        keys = pick_tickers(count)
    elif index_type == "names":
        keys = random_names(count)
    elif index_type == "dates":
        keys = random_date_range(periods=count)
    else:
        keys = [f"item_{i}" for i in range(count)]

    values = random_floats(count, -0.05, 0.05)
    return dict(zip(keys, values))


def messy_dataframe_spec(rows=20):
    """Generate a spec for a messy DataFrame with data quality issues.

    Returns a JSON-serializable dict describing the DataFrame columns and data.
    The agent can use this to create a DataFrame with intentional problems for
    cleaning exercises.
    """
    names = [random.choice(FIRST_NAMES) for _ in range(rows)]
    departments = [random.choice(DEPARTMENTS) for _ in range(rows)]
    salaries = [random.randint(40000, 120000) for _ in range(rows)]
    ages = [random.randint(22, 65) for _ in range(rows)]
    cities = [random.choice(CITIES) for _ in range(rows)]

    # Introduce messiness
    for i in random.sample(range(rows), min(3, rows)):
        names[i] = f"  {names[i]}  "  # whitespace
    for i in random.sample(range(rows), min(2, rows)):
        names[i] = names[i].lower()  # inconsistent case
    for i in random.sample(range(rows), min(2, rows)):
        names[i] = None  # missing values
    for i in random.sample(range(rows), min(3, rows)):
        salaries[i] = "unknown"  # bad type
    for i in random.sample(range(rows), min(2, rows)):
        ages[i] = None  # missing
    for i in random.sample(range(rows), min(2, rows)):
        departments[i] = None  # missing

    # Add duplicates
    if rows > 5:
        dup_idx = random.randint(0, rows - 3)
        names[dup_idx + 1] = names[dup_idx]
        departments[dup_idx + 1] = departments[dup_idx]
        salaries[dup_idx + 1] = salaries[dup_idx]
        ages[dup_idx + 1] = ages[dup_idx]

    return {
        "Name": names,
        "Age": ages,
        "Salary": salaries,
        "Department": departments,
        "City": cities,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate random data for practice questions.")
    parser.add_argument("--type", type=str, required=True,
                        choices=["integers", "floats", "date_range", "names", "series", "messy_dataframe"],
                        help="Type of data to generate.")
    parser.add_argument("--count", type=int, default=10, help="Number of items (default: 10).")
    parser.add_argument("--rows", type=int, default=20, help="Number of rows for dataframe types (default: 20).")
    parser.add_argument("--min", type=float, default=1, dest="min_val", help="Minimum value (default: 1).")
    parser.add_argument("--max", type=float, default=100, dest="max_val", help="Maximum value (default: 100).")
    parser.add_argument("--decimals", type=int, default=4, help="Decimal places for floats (default: 4).")
    parser.add_argument("--start", type=str, default="2020-01-01", help="Start date for date_range.")
    parser.add_argument("--periods", type=int, default=30, help="Number of periods for date_range.")
    parser.add_argument("--freq", type=str, default="D", choices=["D", "B", "W", "M"], help="Frequency for date_range.")
    args = parser.parse_args()

    if args.type == "integers":
        result = random_integers(args.count, int(args.min_val), int(args.max_val))
    elif args.type == "floats":
        result = random_floats(args.count, args.min_val, args.max_val, args.decimals)
    elif args.type == "date_range":
        result = random_date_range(args.start, args.periods, args.freq)
    elif args.type == "names":
        result = random_names(args.count)
    elif args.type == "series":
        result = random_series_data(args.count)
    elif args.type == "messy_dataframe":
        result = messy_dataframe_spec(args.rows)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
