#!/usr/bin/env python3
"""
Generate a random integer between min and max values (inclusive).

Usage:
    python random_int.py --min 1 --max 100
    python random_int.py -n 1 -x 100
"""

import argparse
import random
import sys


def random_int(min_val=None, max_val=None):
    """
    Returns a random integer between min_val and max_val (inclusive).

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        Random integer in range [min_val, max_val]
    """
    return random.randint(min_val, max_val)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a random integer between min and max values"
    )
    parser.add_argument(
        '--min', '-n',
        type=int,
        required=True,
        help='Minimum value (inclusive)'
    )
    parser.add_argument(
        '--max', '-x',
        type=int,
        required=True,
        help='Maximum value (inclusive)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional)'
    )

    args = parser.parse_args()

    if args.min > args.max:
        print(f"Error: min ({args.min}) cannot be greater than max ({args.max})")
        sys.exit(1)

    if args.seed is not None:
        random.seed(args.seed)

    result = random_int(min_val=args.min, max_val=args.max)
    print(result)


if __name__ == "__main__":
    main()