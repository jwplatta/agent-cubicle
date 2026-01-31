#!/usr/bin/env python3
"""
Enrich question templates by replacing placeholders with generated values.

Takes a question string with placeholders like:
    {{random_int(min_val=1, max_val=10)}}

And replaces them with actual random values by calling the functions directly.

Usage:
    python enrich_question.py --question "A committee of {{random_int(min_val=1, max_val=10)}} people..."
    python enrich_question.py -q "How many ways to arrange {{random_int(min_val=5, max_val=10)}} items?"

    # With seed for reproducibility
    python enrich_question.py --question "..." --seed 42
"""

import argparse
import re
import sys
from random_int import random_int


def parse_random_int_call(placeholder_text):
    """
    Parse a random_int placeholder and extract min/max values.

    Supports formats:
        - random_int(min_val=1, max_val=10)
        - random_int(min=1, max=10)

    Args:
        placeholder_text: The text inside {{ }}

    Returns:
        Tuple of (min_val, max_val) or (None, None) if parsing fails
    """
    min_val = None
    max_val = None

    # Extract the part inside parentheses
    match = re.search(r'random_int\((.*?)\)', placeholder_text)
    if match:
        args_str = match.group(1)
        # Parse keyword arguments
        # Handle both min_val= and min=
        min_match = re.search(r'min(?:_val)?=(\d+)', args_str)
        max_match = re.search(r'max(?:_val)?=(\d+)', args_str)

        if min_match:
            min_val = int(min_match.group(1))
        if max_match:
            max_val = int(max_match.group(1))

    return min_val, max_val


def enrich_question(question_text, seed=None):
    """
    Replace all placeholders in a question with generated values.

    Args:
        question_text: Question string with {{...}} placeholders
        seed: Optional random seed for reproducibility

    Returns:
        Enriched question string with placeholders replaced
    """
    if seed is not None:
        import random
        random.seed(seed)

    # Pattern to match {{ ... }}
    pattern = r'\{\{([^}]+)\}\}'

    def replace_placeholder(match):
        """Replace a single placeholder with its generated value."""
        placeholder = match.group(1).strip()

        if 'random_int' in placeholder:
            min_val, max_val = parse_random_int_call(placeholder)

            if min_val is not None and max_val is not None:
                result = random_int(min_val, max_val)
                return str(result)
            else:
                print(f"Warning: Could not parse placeholder: {{{{{placeholder}}}}}", file=sys.stderr)
                return match.group(0)  # Return unchanged

        # Add support for other generators here in the future
        # elif 'random_float' in placeholder:
        #     ...

        # Unknown placeholder type
        print(f"Warning: Unknown placeholder type: {{{{{placeholder}}}}}", file=sys.stderr)
        return match.group(0)  # Return unchanged

    enriched = re.sub(pattern, replace_placeholder, question_text)
    return enriched


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enrich question templates by replacing placeholders with generated values"
    )
    parser.add_argument(
        '--question', '-q',
        type=str,
        required=True,
        help='Question text with {{...}} placeholders'
    )
    parser.add_argument(
        '--seed',
        type=int,
        required=False,
        help='Random seed for reproducibility (optional)'
    )

    args = parser.parse_args()

    enriched = enrich_question(args.question, seed=args.seed)

    print(enriched)


if __name__ == "__main__":
    main()
