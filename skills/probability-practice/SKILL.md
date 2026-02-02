---
name: probability-practice
description: Generate Jupyter notebook practice challenges for probability. Use when the user wants practice problems for probability, statistics, contingency tables, Bayes theorem, or conditional probability.
allowed-tools: Read, Grep, Glob, Write, Bash, AskUserQuestion
---

# Probability Practice

Generate a Jupyter notebook filled with hand-solvable probability challenges. Problems use **2×2 contingency tables** with small integer counts to practice marginal probability, conditional probability, Bayes' theorem, and independence testing.

Note that all resoures for creating these notebooks are located in the user level skills folder for the agent:
- If you are codex, look in ~/.codex/skills/probability-practice
- If you are claude, look in ~/.claude/skills/probability-practice
- If you are copilot, look in ~/.copilot/skills/probability-practice
- If you are gemini, look in ~/.gemini/skills/probability-practice

## Workflow

1. **Gather parameters** using AskUserQuestion. Ask the user:
   - **Category**: Which category to focus on. Available categories:
     - counting (define the sample space)
     - marginals (sum out variables)
     - joint (multiply probabilities correctly)
     - conditional (normalize correctly)
     - bayes (reverse conditioning)
     - independence (recognize factorization)
     - total_probability (decompose mixtures)
     - expectation
     - variance
   - **Difficulty**: easy, medium, or hard.
   - **Number of questions**: How many challenges to include (default 10).
   - **Output directory**: Where to save the notebook. Default is the current working directory.
   - **Previous exercises folder** (optional): Path to a folder containing previous practice notebooks. If provided, scan these notebooks to avoid repeating exact questions. You may generate the same *type* of question but must vary the table data to ensure uniqueness.

2. **Check for previous exercises** (if folder provided):
   - Scan notebooks in the previous exercises folder for question prompts.
   - Extract the core challenge type from each (e.g., "compute P(A)", "test independence").
   - When generating new questions, avoid repeating the exact same prompt. You may reuse the same question *type* but must generate different table data (different cell counts) to make it fresh.

3. **Generate varied problem data** using `probability_generators.py` (see [Scripts](#scripts) below). For every notebook:
   - Each question uses the `JointTableGenerator` to create a random 2×2 contingency table.
   - Tables have different total counts (20, 30, 40, 50, 60, 100) to vary the arithmetic.
   - Cell counts are randomly generated ensuring all cells are positive (no empty rows/columns).
   - The `ensure_simple_fractions` parameter adjusts counts to produce clean fractions when possible.
   - Every time you generate a notebook, the tables will be different, ensuring no two notebooks are identical.

4. **Build the notebook** using `generate_probability_notebook.py`:
   ```bash
   python scripts/generate_probability_notebook.py \
     --bank questions/bank.json \
     --category marginals \
     --difficulty easy \
     --count 8 \
     --output ./notebooks
   ```
   - Use `--category` to specify the category (marginals, conditional, bayes, independence, etc.).
   - Use `--difficulty` to filter by difficulty (easy, medium, hard) or omit for mixed.
   - Use `--count` to specify the number of problems.
   - Use `--template` to specify a custom template (default: `templates/probability_template.ipynb`).
   - Use `--seed` for reproducible random generation (optional).

5. **Template processing rules**:
   - The template (`templates/probability_template.ipynb`) contains an example challenge for demonstration purposes.
   - **IMPORTANT**: Example cells are automatically removed from generated notebooks. Any cell with `"example"` in its cell ID will be filtered out.
   - This ensures students only see their practice problems, not the template example.
   - When modifying the template, mark all example cells with IDs containing "example" (e.g., `"example-title"`, `"example-solution"`).

6. **Customize the setup cell** — The template includes a `check_prob()` helper function that students can use to verify their answers. This function is pre-loaded in the setup cell and ready to use.

7. **Confirm** the notebook path to the user when finished.

## Notebook Structure

Each generated notebook follows this structure:

1. **Title cell** (markdown): includes difficulty, date, number of questions, and subcategories covered.
2. **Setup cell** (code): import statements (numpy, pandas, fractions, matplotlib) and the `check_prob()` helper function for verifying answers.
3. **For each question**:
   - A **markdown cell** with the challenge prompt, numbered (e.g. "## Challenge 1"). Includes:
     - The contingency table (formatted as markdown table)
     - A clear problem statement
     - A **hidden hint** wrapped in a `<details><summary>Hint</summary>...</details>` tag
   - An **empty code cell** for the user to write their solution or use `check_prob()`.
   - A **hidden solution cell** wrapped in a markdown `<details><summary>Solution</summary>...</details>` tag so the user can reveal it.

### DO NOT
1. Include summaries at the end of the notebook.
2. Use simulation or Monte Carlo methods — all problems must be solvable with exact arithmetic.
3. Include example challenges from the template in the final notebook (they are automatically filtered out).

## Scripts

All scripts live in [scripts/](scripts/) and are run from that directory.

### `generate_probability_notebook.py`

Builds a `.ipynb` file from the question bank + generated table data. Uses `nbformat`.

```bash
# Generate 8 easy marginal probability problems:
python scripts/generate_probability_notebook.py \
  --bank questions/bank.json \
  --category joint_probability \
  --subcategory marginals \
  --difficulty easy \
  --count 8 \
  --output ./notebooks

# Generate 10 mixed difficulty conditional probability problems:
python scripts/generate_probability_notebook.py \
  --bank questions/bank.json \
  --category joint_probability \
  --subcategory conditional \
  --count 10 \
  --output ./notebooks

# Generate 5 hard problems mixing all subcategories:
python scripts/generate_probability_notebook.py \
  --bank questions/bank.json \
  --category joint_probability \
  --difficulty hard \
  --count 5 \
  --output ./notebooks

# Use a seed for reproducible generation:
python scripts/generate_probability_notebook.py \
  --bank questions/bank.json \
  --category joint_probability \
  --subcategory bayes \
  --difficulty medium \
  --count 6 \
  --seed 42 \
  --output ./notebooks
```

**Dependencies:** `nbformat`, `json`, `argparse`, `datetime`

### `probability_generators.py`

Contains the `JointTableGenerator` class for creating 2×2 contingency tables.

```python
from probability_generators import JointTableGenerator

gen = JointTableGenerator(seed=42)  # Optional seed for reproducibility

# Generate a random 2×2 table with total count 20
table = gen.generate_2x2(total=20, ensure_simple_fractions=True)

# Returns dict with:
# - a, b, c, d: cell counts
# - total: N
# - table_str: formatted markdown table
# - marginal_A, marginal_B, marginal_notA, marginal_notB
# - joint_AB, joint_A_notB, joint_notA_B, joint_notA_notB
```

**Key parameters:**
- `total`: Total count N (default: 20). Use 20, 30, 40, 50, 60, or 100 for clean fractions.
- `ensure_simple_fractions`: If True, adjusts counts to avoid ugly fractions (default: True).

**Table format:**
```
         B      ¬B    Total
A        a      b     a+b
¬A       c      d     c+d
Total   a+c    b+d     N
```

### `fraction_utils.py`

Helper functions for working with fractions and probabilities.

```python
from fraction_utils import simplify_fraction, format_probability, check_probability

# Simplify a fraction
num, denom = simplify_fraction(12, 20)  # Returns (3, 5)

# Format probability as "a/b = 0.xxxx"
result = format_probability(3, 4)  # Returns "3/4 = 0.7500"

# Check user answer (for use in notebooks)
check_probability("3/4", 3, 4)  # Returns True, prints confirmation
check_probability(0.75, 3, 4)   # Also accepts floats
```

## Templates

Category-specific notebook templates live in [templates/](templates/).

| Template | File | Description |
|----------|------|-------------|
| Probability | `templates/probability_template.ipynb` | Imports numpy, pandas, fractions, matplotlib. Includes `check_prob()` helper and example challenge. |

The template includes:
- Title cell with placeholders: `{{difficulty}}`, `{{date}}`, `{{count}}`, `{{subcategories}}`
- Setup cell with imports and `check_prob()` function
- Example challenge showing expected format (automatically removed from generated notebooks)
- Instructions for students (solve by hand first, verify with Python)

**Template editing guidelines:**
- Mark all example cells with IDs containing "example" (e.g., `id="example-title"`)
- These cells will be automatically filtered out when generating notebooks
- Only cells marked with "example" in the ID will be removed; all other cells are preserved

## Question Bank

Pre-written questions are stored in [questions/bank.json](questions/bank.json). The bank is organized as:

```
{ category: { subcategory: { difficulty: [question, ...] } } }
```

Each question has:
- `prompt_template`: Template string with `{{placeholder}}` for generated values
- `generator`: Name of generator function ("joint_table_2x2")
- `generator_params`: Parameters to pass to generator (total, ensure_simple_fractions)
- `query_type`: Type of question (marginal_A, conditional_A_given_B, etc.)
- `solution_template`: Template for solution with `{{placeholder}}` for computed values
- `hint`: Hint text to help students
- `topics`: List of topic tags

The generator fills in placeholders with actual values from randomly generated tables.

## Categories

Refer to [references/PROBABILITY_AND_STATS.md](references/PROBABILITY_AND_STATS.md) for detailed probability concepts and [references/FORMULAS.md](references/FORMULAS.md) for formula quick reference. Use [examples/PROBABILITY_EXAMPLES.md](examples/PROBABILITY_EXAMPLES.md) for worked examples.

Available categories:
- **Marginals**: P(A), P(B), P(¬A), P(¬B), P(A ∪ B), complement rules, law of total probability
- **Conditional**: P(A|B), P(B|A), P(A|¬B), conditional complement rules, multiplication rule
- **Bayes**: Bayes' theorem, prior/posterior/likelihood, diagnostic tests (sensitivity, specificity, PPV, NPV), odds ratio
- **Independence**: Testing P(A ∩ B) = P(A) × P(B), testing P(A|B) = P(A), chi-squared statistic, expected counts

## Difficulty Levels

- **Easy**: Single-step calculations (1-5 lines of work). Focus on one concept: find a marginal, compute a conditional probability, apply a formula directly. Provide hints. Expect simple arithmetic with clean fractions.

- **Medium**: Multi-step problems (2-3 steps). Combine concepts: compute several probabilities then compare, verify laws (complement, total probability), use Bayes' theorem with all components. Provide hints. Expect 5-10 lines of work.

- **Hard**: Complex multi-step problems requiring careful reasoning. Test all three definitions of independence, compute all conditional probabilities and verify relationships, apply law of total probability then Bayes' theorem, diagnostic test problems with all metrics. May provide hints. Expect 10-20+ lines of work.

## Problem Design Principles

1. **Hand-solvable**: All problems use small integer counts (typically totals of 20-100). No decimal approximations needed.

2. **Exact arithmetic**: No simulation, no Monte Carlo, no rounding. Students should get exact fractional answers.

3. **Randomized data**: Every notebook generation creates different tables. No two students get identical problems.

4. **Clean fractions**: The generator adjusts cell counts to produce fractions with small denominators when possible (denominators from {2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30, 40, 50, 60, 100}).

5. **Progressive difficulty**:
   - Easy: Direct lookup or single calculation
   - Medium: Multiple calculations or applying a theorem
   - Hard: Verification, proof, or multi-step reasoning

6. **Pedagogical focus**: Problems emphasize understanding relationships between probabilities, not computational tricks.

## Verification

The `check_prob()` function in the notebook setup cell allows students to verify their answers:

```python
# After solving by hand: P(A) = 3/5
check_prob('3/5', 3, 5)  # ✓ Correct! 3/5 = 0.6000

# Also accepts floats:
check_prob(0.6, 3, 5)    # ✓ Correct! 3/5 = 0.6000

# Shows error if wrong:
check_prob('1/2', 3, 5)  # ✗ Your answer: 1/2 = 0.5000
                         #   Correct: 3/5 = 0.6000
```

This encourages students to:
1. Solve problems by hand first
2. Show their work in markdown or comments
3. Use Python only to verify their manual calculations

## Additional Resources

- For probability theory and concepts, see [references/PROBABILITY_AND_STATS.md](references/PROBABILITY_AND_STATS.md)
- For formula quick reference, see [references/FORMULAS.md](references/FORMULAS.md)
- For worked examples showing expected format and detail, see [examples/PROBABILITY_EXAMPLES.md](examples/PROBABILITY_EXAMPLES.md)
- For the mathematical framework behind problem generation, see `doc/PROBABILITY_PROBLEM_GENERATION.md` in the repository root

## Future Enhancements

The current MVP implementation focuses on 2×2 contingency tables with joint probability problems. Future versions may add:

- Naive Bayes classification problems (multiple features)
- Counting problems (permutations, combinations, sampling)
- Discrete random variables (expected value, variance, distributions)
- Binomial and Poisson distributions
- Normal approximations

All future problems will maintain the core principles: hand-solvable, exact arithmetic, randomized data, and pedagogical focus.
