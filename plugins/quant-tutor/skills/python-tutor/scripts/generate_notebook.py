#!/usr/bin/env python3
"""Generate a Jupyter notebook with Python practice challenges.

Reads a category-specific template notebook, then appends question cells
sourced from either a question bank JSON, a questions JSON file, or stdin.

Usage:
    # Pull random questions from the built-in question bank:
    python generate_notebook.py --bank ../questions/bank.json \
        --category pandas --subcategory series \
        --difficulty easy --count 5 --output ./notebooks

    # From a questions JSON file (Claude-generated):
    python generate_notebook.py --questions questions.json \
        --category pandas --difficulty medium --output ./notebooks

    # From stdin (Claude pipes generated questions):
    cat questions.json | python generate_notebook.py \
        --category algorithms --difficulty hard --output ./notebooks
"""

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

import nbformat

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

TEMPLATE_MAP = {
    "pandas": TEMPLATES_DIR / "pandas_template.ipynb",
    "algorithms": TEMPLATES_DIR / "algorithms_template.ipynb",
}


def load_template(category):
    """Load the template notebook for a category."""
    template_path = TEMPLATE_MAP.get(category)
    if not template_path or not template_path.exists():
        # Fall back to pandas template for mixed/unknown
        template_path = TEMPLATE_MAP["pandas"]

    with open(template_path) as f:
        nb = nbformat.read(f, as_version=4)
    return nb


def fill_template_vars(nb, difficulty, count, subcategories):
    """Replace {{placeholders}} in the template title cell."""
    today = date.today().isoformat()
    replacements = {
        "{{difficulty}}": difficulty.capitalize(),
        "{{date}}": today,
        "{{count}}": str(count),
        "{{subcategories}}": subcategories or "All",
    }
    # Only replace in the first markdown cell (title cell)
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            source = cell.source
            for placeholder, value in replacements.items():
                source = source.replace(placeholder, value)
            cell.source = source
            break


def make_question_cells(questions, difficulty):
    """Create notebook cells for each question.

    Each question produces:
      1. Markdown cell with the challenge prompt
      2. Empty code cell for the user's solution
      3. Markdown cell with hidden solution in <details> tag
    """
    cells = []
    for i, q in enumerate(questions, 1):
        subcat = q.get("subcategory", "")
        subcat_tag = f" *({subcat})*" if subcat else ""

        # Challenge prompt
        prompt = f"### Challenge {i}{subcat_tag}\n\n{q['prompt']}"
        if q.get("hint") and difficulty in ("easy", "medium"):
            prompt += f"\n\n**Hint:** {q['hint']}"

        cells.append(nbformat.v4.new_markdown_cell(prompt))

        # Per-question setup code (optional)
        if q.get("setup"):
            cells.append(nbformat.v4.new_code_cell(q["setup"]))

        # Empty answer cell
        cells.append(nbformat.v4.new_code_cell("# Your solution here\n"))

        # Hidden solution
        solution_md = (
            "<details>\n"
            "<summary><b>Solution</b></summary>\n\n"
            "```python\n"
            f"{q['solution']}\n"
            "```\n\n"
            "</details>"
        )
        cells.append(nbformat.v4.new_markdown_cell(solution_md))

    return cells


def load_from_bank(bank_path, category=None, subcategory=None, difficulty=None, count=10):
    """Load and filter questions from a question bank JSON file.

    Bank structure:
    {
        "pandas": {
            "series": {
                "easy": [{"prompt": "...", "solution": "...", "hint": "..."}, ...],
                "medium": [...],
                "hard": [...]
            },
            ...
        },
        "algorithms": { ... }
    }
    """
    with open(bank_path) as f:
        bank = json.load(f)

    pool = []
    categories = [category] if category and category in bank else list(bank.keys())

    for cat in categories:
        subcategories = bank[cat]
        subs = (
            [subcategory]
            if subcategory and subcategory in subcategories
            else list(subcategories.keys())
        )
        for sub in subs:
            difficulties = subcategories[sub]
            diffs = (
                [difficulty]
                if difficulty and difficulty in difficulties
                else list(difficulties.keys())
            )
            for diff in diffs:
                for q in difficulties.get(diff, []):
                    q_copy = dict(q)
                    q_copy.setdefault("subcategory", sub)
                    pool.append(q_copy)

    if not pool:
        print("No questions matched the filters.", file=sys.stderr)
        sys.exit(1)

    random.shuffle(pool)
    return pool[:count]


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Jupyter notebook with Python practice challenges."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--questions", type=str, help="Path to a JSON file with a list of question objects."
    )
    source.add_argument(
        "--bank", type=str, help="Path to the question bank JSON. Use with --category, --subcategory, --difficulty, --count."
    )
    parser.add_argument("--category", type=str, default="", help="Category: pandas, algorithms, or empty for mixed.")
    parser.add_argument("--subcategory", type=str, default="", help="Subcategory filter (e.g. 'series', 'sorting').")
    parser.add_argument("--difficulty", type=str, default="medium", help="Difficulty: easy, medium, hard (default: medium).")
    parser.add_argument("--count", type=int, default=10, help="Number of questions (default: 10).")
    parser.add_argument("--output", type=str, default=".", help="Output directory for the notebook.")
    args = parser.parse_args()

    # Load questions
    if args.bank:
        questions = load_from_bank(
            args.bank,
            category=args.category or None,
            subcategory=args.subcategory or None,
            difficulty=args.difficulty or None,
            count=args.count,
        )
    elif args.questions:
        with open(args.questions) as f:
            questions = json.load(f)
    else:
        questions = json.load(sys.stdin)

    if not questions:
        print("No questions provided.", file=sys.stderr)
        sys.exit(1)

    category = args.category or "mixed"
    difficulty = args.difficulty or "medium"

    # Build notebook from template
    nb = load_template(category)
    fill_template_vars(nb, difficulty, len(questions), args.subcategory)

    # Append question cells
    question_cells = make_question_cells(questions, difficulty)
    nb.cells.extend(question_cells)

    # Write output
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    filename = f"python_practice_{category}_{difficulty}_{today}.ipynb"
    output_path = output_dir / filename

    # Normalize to add cell IDs (required by nbformat 5+)
    _, nb = nbformat.validator.normalize(nb)

    with open(output_path, "w") as f:
        nbformat.write(nb, f)

    print(f"Notebook generated: {output_path}")


if __name__ == "__main__":
    main()
