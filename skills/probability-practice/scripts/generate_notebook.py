#!/usr/bin/env python3
"""
Generate Jupyter notebooks with probability practice questions.

Usage:
    python generate_notebook.py --topics combinations permutations --count 10 --output practice.ipynb
    python generate_notebook.py --topics combinations --count 5 --output practice.ipynb --seed 42
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    import nbformat
    from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
except ImportError:
    print("Error: nbformat not installed. Run: pip install nbformat")
    sys.exit(1)

from question_randomizer import select_questions


def create_notebook(questions, title="Probability Practice"):
    """
    Create a Jupyter notebook from enriched questions.

    Args:
        questions: List of question dictionaries from question_randomizer
        title: Notebook title

    Returns:
        nbformat NotebookNode
    """
    nb = new_notebook()

    # Add title cell
    date_str = datetime.now().strftime("%Y-%m-%d")
    topics = list(set(q['topic'] for q in questions))
    title_md = f"# {title}\n\n**Date:** {date_str}\n\n**Questions:** {len(questions)}\n\n**Topics:** {', '.join(topics)}"
    nb.cells.append(new_markdown_cell(title_md))

    # Add each question
    for i, q in enumerate(questions, 1):
        # Question markdown cell
        question_md = f"---\n\n## Problem {i}\n\n**Topic:** {q['topic']}\n\n{q['question']}"
        nb.cells.append(new_markdown_cell(question_md))

        # Empty code cell for student work
        nb.cells.append(new_code_cell("# Your solution here:\n\n"))

        # Solution cell (if available)
        if q.get('solution') and q['solution'].strip():
            solution_md = f"<details>\n<summary><b>Solution</b> (click to expand)</summary>\n\n{q['solution']}\n\n</details>"
            nb.cells.append(new_markdown_cell(solution_md))

    return nb


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Jupyter notebooks with probability practice questions"
    )
    parser.add_argument(
        '--topics',
        nargs='+',
        required=True,
        choices=['combinations', 'permutations'],
        help='Topic names (currently available: combinations, permutations)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of questions to include (default: 10)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output notebook file path (.ipynb)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional)'
    )
    parser.add_argument(
        '--title',
        default='Probability Practice',
        help='Notebook title (default: Probability Practice)'
    )

    args = parser.parse_args()

    # Ensure output has .ipynb extension
    output_path = Path(args.output)
    if output_path.suffix != '.ipynb':
        output_path = output_path.with_suffix('.ipynb')

    # Get enriched questions using question_randomizer
    print(f"Selecting {args.count} questions from topics: {', '.join(args.topics)}")
    questions = select_questions(
        topics=args.topics,
        count=args.count,
        seed=args.seed
    )

    # Create notebook
    nb = create_notebook(questions, title=args.title)

    # Save notebook
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        nbformat.write(nb, f)

    print(f"\n✓ Created notebook with {len(questions)} questions: {output_path}")
    print(f"✓ Topics: {', '.join(args.topics)}")
    print(f"\nOpen with: jupyter notebook {output_path}")


if __name__ == '__main__':
    main()
