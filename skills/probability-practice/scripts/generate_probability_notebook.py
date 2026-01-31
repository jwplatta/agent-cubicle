#!/usr/bin/env python3
"""
Generate randomized probability practice notebooks from question bank.

Usage:
    python generate_probability_notebook.py \\
        --bank questions/bank.json \\
        --category joint_probability \\
        --subcategory marginals \\
        --difficulty easy \\
        --count 8 \\
        --output ./notebooks
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import nbformat for creating Jupyter notebooks
try:
    import nbformat
    from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
except ImportError:
    print("Error: nbformat not installed. Run: pip install nbformat")
    sys.exit(1)

# Import local modules
from probability_generators import JointTableGenerator
from fraction_utils import simplify_fraction, format_probability

# Valid question bank categories
VALID_CATEGORIES = [
    'counting',
    'marginals',
    'joint',
    'conditional',
    'bayes',
    'independence',
    'total_probability',
    'expectation',
    'variance',
    'covariance'
]


class NotebookGenerator:
    """Generate probability practice notebooks from question bank."""

    def __init__(self, bank_path: str, seed: int = None):
        """
        Initialize generator.

        Args:
            bank_path: Path to questions/bank.json
            seed: Random seed for reproducibility
        """
        self.bank_path = Path(bank_path)
        self.bank = self._load_bank()
        self.generator = JointTableGenerator(seed=seed)

        if seed is not None:
            random.seed(seed)

    def _load_bank(self) -> Dict:
        """Load question bank from JSON file."""
        if not self.bank_path.exists():
            raise FileNotFoundError(f"Question bank not found: {self.bank_path}")

        with open(self.bank_path, 'r') as f:
            return json.load(f)

    def filter_questions(
        self,
        category: str,
        difficulty: str = None
    ) -> List[Dict]:
        """
        Filter questions by category and difficulty.

        Args:
            category: Category (e.g., 'marginals', 'conditional', 'bayes', 'independence')
            difficulty: Optional difficulty ('easy', 'medium', 'hard')

        Returns:
            List of matching questions
        """
        if category not in self.bank:
            valid_cats = ', '.join(VALID_CATEGORIES)
            raise ValueError(
                f"Category '{category}' not found in bank.\n"
                f"Valid categories: {valid_cats}"
            )

        questions = []

        if difficulty:
            # Specific difficulty within category
            if difficulty not in self.bank[category]:
                raise ValueError(
                    f"Difficulty '{difficulty}' not found in '{category}'"
                )
            questions = self.bank[category][difficulty]
        else:
            # All difficulties in category
            for diff in self.bank[category]:
                questions.extend(self.bank[category][diff])

        return questions

    def generate_problem_data(self, question: Dict) -> Dict:
        """
        Generate random data for a question using its generator.

        Args:
            question: Question dictionary from bank

        Returns:
            Dictionary with generated data and filled templates
        """
        generator_name = question['generator']
        generator_params = question.get('generator_params', {})

        # Call appropriate generator
        if generator_name == 'joint_table_2x2':
            data = self.generator.generate_2x2(**generator_params)
        elif generator_name == 'joint_table_3x3':
            data = self.generator.generate_3x3(**generator_params)
        else:
            raise ValueError(f"Unknown generator: {generator_name}")

        # Add 'table' alias for 'table_str' for template compatibility
        if 'table_str' in data:
            data['table'] = data['table_str']

        # Fill in prompt template
        prompt = question['prompt_template']
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            prompt = prompt.replace(placeholder, str(value))

        # Generate solution based on query type
        solution = self._generate_solution(question, data)

        return {
            'prompt': prompt,
            'solution': solution,
            'hint': question.get('hint', 'No hint available.'),
            'data': data,
            'topics': question.get('topics', [])
        }

    def _generate_solution(self, question: Dict, data: Dict) -> str:
        """
        Generate solution text with calculations.

        Args:
            question: Question dictionary
            data: Generated problem data

        Returns:
            Formatted solution string
        """
        query_type = question.get('query_type', '')
        solution_template = question.get('solution_template', '')

        # Calculate derived values based on query type
        values = data.copy()

        # Add simplified fractions
        if 'marginal_A' in data:
            num, denom = simplify_fraction(data['marginal_A'], data['total'])
            values['prob_A'] = format_probability(data['marginal_A'], data['total'])
            values['simplified'] = format_probability(data['marginal_A'], data['total'])

        if 'marginal_B' in data:
            values['prob_B'] = format_probability(data['marginal_B'], data['total'])

        if 'joint_AB' in data and 'marginal_B' in data:
            values['prob_A_given_B'] = format_probability(data['joint_AB'], data['marginal_B'])

        if 'joint_AB' in data and 'marginal_A' in data:
            values['prob_B_given_A'] = format_probability(data['joint_AB'], data['marginal_A'])

        # Conditional probabilities
        if query_type == 'conditional_A_given_B':
            values['simplified'] = format_probability(data['joint_AB'], data['marginal_B'])

        if query_type == 'conditional_B_given_A':
            values['simplified'] = format_probability(data['joint_AB'], data['marginal_A'])

        if query_type == 'conditional_notA_given_B':
            values['simplified'] = format_probability(data['joint_notA_B'], data['marginal_B'])

        # Union
        if query_type in ['union', 'union_verification']:
            union_count = data['joint_AB'] + data['joint_A_notB'] + data['joint_notA_B']
            values['union_count'] = union_count
            values['simplified'] = format_probability(union_count, data['total'])

        # Comparisons
        if 'comparison' in query_type or query_type == 'marginal_both':
            if data['marginal_A'] == data['marginal_B']:
                values['comparison'] = "Yes, P(A) = P(B)"
            else:
                values['comparison'] = "No, P(A) ≠ P(B)"

        if query_type == 'conditional_both':
            prob_a_b = data['joint_AB'] / data['marginal_B']
            prob_b_a = data['joint_AB'] / data['marginal_A']
            if abs(prob_a_b - prob_b_a) < 0.0001:
                values['comparison'] = "Yes, P(A|B) = P(B|A)"
            else:
                values['comparison'] = "No, P(A|B) ≠ P(B|A)"

        if query_type == 'conditional_comparison':
            prob_a_given_b = data['joint_AB'] / data['marginal_B']
            prob_a_given_notb = data['joint_A_notB'] / data['marginal_notB']
            values['prob_A_given_notB'] = format_probability(data['joint_A_notB'], data['marginal_notB'])

            if prob_a_given_b > prob_a_given_notb:
                values['comparison'] = "A is more likely given B than given ¬B"
            elif prob_a_given_b < prob_a_given_notb:
                values['comparison'] = "A is more likely given ¬B than given B"
            else:
                values['comparison'] = "A has the same probability given B or ¬B"

        # Independence tests
        if 'independence' in query_type:
            product = data['marginal_A'] * data['marginal_B']
            joint_times_total = data['joint_AB'] * data['total']

            values['product_num'] = product
            values['total_squared'] = data['total'] * data['total']

            if product == joint_times_total:
                values['independence_conclusion'] = "A and B are independent."
            else:
                values['independence_conclusion'] = "A and B are NOT independent."

        # Counting operations
        if query_type == 'count_union':
            union_count = data['joint_AB'] + data['joint_A_notB'] + data['joint_notA_B']
            values['union_count'] = union_count

        if query_type == 'combinations':
            n = data['total']
            k = 2
            values['minus_2'] = n - 2
            values['minus_1'] = n - 1
            values['combination_result'] = (n * (n - 1)) // 2

        if query_type == 'permutations_all':
            import math
            values['factorial_result'] = math.factorial(data['total'])

        # Joint probability operations
        if query_type == 'joint_A_notB':
            values['simplified'] = format_probability(data['joint_A_notB'], data['total'])

        if query_type == 'joint_notA_notB':
            values['simplified'] = format_probability(data['joint_notA_notB'], data['total'])

        # Expectation operations
        if query_type == 'expectation_indicator_A':
            values['simplified'] = format_probability(data['marginal_A'], data['total'])

        if query_type == 'expectation_scaled_indicator':
            values['expectation_result'] = format_probability(10 * data['marginal_B'], data['total'])

        if query_type == 'expectation_sum':
            values['expectation_sum'] = data['marginal_A'] + data['marginal_B']

        if query_type == 'expectation_custom_rv':
            exactly_one = data['joint_A_notB'] + data['joint_notA_B']
            values['exactly_one'] = exactly_one
            values['ez_term1'] = 100 * data['joint_AB']
            values['ez_term2'] = 50 * exactly_one
            values['expectation_z'] = 100 * data['joint_AB'] + 50 * exactly_one

        # Variance operations
        if query_type == 'variance_indicator':
            p = data['marginal_A'] / data['total']
            variance = p * (1 - p)
            values['variance_result'] = f"{variance:.4f}"

        if query_type == 'variance_sum_independent':
            p_a = data['marginal_A'] / data['total']
            p_b = data['marginal_B'] / data['total']
            var_x = p_a * (1 - p_a)
            var_y = p_b * (1 - p_b)
            values['var_x'] = f"{var_x:.4f}"
            values['var_y'] = f"{var_y:.4f}"
            values['var_sum'] = f"{var_x + var_y:.4f}"

        # Covariance operations
        if 'covariance' in query_type:
            product = data['marginal_A'] * data['marginal_B']
            joint_times_total = data['joint_AB'] * data['total']
            values['product_num'] = product
            values['total_squared'] = data['total'] * data['total']

            # Covariance calculation
            e_xy = data['joint_AB'] / data['total']
            e_x = data['marginal_A'] / data['total']
            e_y = data['marginal_B'] / data['total']
            cov = e_xy - e_x * e_y
            values['covariance_result'] = f"{cov:.4f}"

            if query_type == 'covariance_independence_test':
                if product == joint_times_total:
                    values['independence_test'] = "A and B ARE independent."
                    values['covariance_conclusion'] = "Since A and B are independent, Cov(X,Y) = 0 ✓"
                else:
                    values['independence_test'] = "A and B are NOT independent."
                    values['covariance_conclusion'] = "Since A and B are dependent, Cov(X,Y) ≠ 0"

        # Fill template
        solution = solution_template
        for key, value in values.items():
            placeholder = f"{{{{{key}}}}}"
            solution = solution.replace(placeholder, str(value))

        return solution

    def create_notebook(
        self,
        questions: List[Dict],
        count: int,
        difficulty: str,
        category: str,
        template_path: str = None
    ) -> nbformat.NotebookNode:
        """
        Create a Jupyter notebook with selected questions.

        Args:
            questions: List of question dictionaries
            count: Number of questions to include
            difficulty: Difficulty level string
            category: Category name
            template_path: Path to template notebook (optional)

        Returns:
            nbformat NotebookNode
        """
        # Load template if provided
        if template_path:
            template_path = Path(template_path)
            if template_path.exists():
                with open(template_path, 'r') as f:
                    nb = nbformat.read(f, as_version=4)
            else:
                raise FileNotFoundError(f"Template not found: {template_path}")
        else:
            nb = new_notebook()

        # Sample questions
        if len(questions) > count:
            sampled = random.sample(questions, count)
        else:
            sampled = questions

        # Fill template placeholders
        date_str = datetime.now().strftime("%Y-%m-%d")
        category_str = category if category else "mixed"

        # Remove example challenge cells (they're just for the template)
        # Keep only cells that don't have "example" in their cell ID
        filtered_cells = []
        for cell in nb.cells:
            cell_id = cell.get('id', '')
            # Keep cells that aren't part of the example challenge
            if 'example' not in cell_id.lower():
                # Replace placeholders in kept cells
                if cell.cell_type == 'markdown':
                    cell.source = cell.source.replace('{{difficulty}}', difficulty.title())
                    cell.source = cell.source.replace('{{date}}', date_str)
                    cell.source = cell.source.replace('{{count}}', str(len(sampled)))
                    cell.source = cell.source.replace('{{category}}', category_str)
                filtered_cells.append(cell)

        nb.cells = filtered_cells

        # Add question cells
        for i, question in enumerate(sampled, 1):
            problem_data = self.generate_problem_data(question)

            # Markdown cell with question
            question_md = f"---\n\n## Challenge {i}\n\n{problem_data['prompt']}\n\n"
            question_md += f"<details>\n<summary><b>Hint</b> (click to expand)</summary>\n\n"
            question_md += f"{problem_data['hint']}\n\n</details>"

            nb.cells.append(new_markdown_cell(question_md))

            # Empty code cell for student work
            nb.cells.append(new_code_cell("# Your solution here:\n\n"))

            # Hidden solution cell (markdown)
            solution_md = f"<details>\n<summary><b>Solution</b> (click to expand)</summary>\n\n"
            solution_md += f"**Solution:**\n\n{problem_data['solution']}\n\n</details>"

            nb.cells.append(new_markdown_cell(solution_md))

        return nb

    def save_notebook(self, nb: nbformat.NotebookNode, output_path: Path):
        """
        Save notebook to file.

        Args:
            nb: Notebook object
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            nbformat.write(nb, f)

        print(f"✓ Notebook saved: {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate probability practice notebooks"
    )
    parser.add_argument(
        '--bank',
        default='questions/bank.json',
        help='Path to question bank JSON (default: questions/bank.json)'
    )
    parser.add_argument(
        '--category',
        choices=VALID_CATEGORIES,
        help=f'Question category. Valid options: {", ".join(VALID_CATEGORIES)}'
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        help='Difficulty level (optional)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=8,
        help='Number of questions (default: 8)'
    )
    parser.add_argument(
        '--output',
        default='./notebooks',
        help='Output directory (default: ./notebooks)'
    )

    # Default template path relative to this script's directory
    script_dir = Path(__file__).parent
    default_template = script_dir.parent / 'templates' / 'probability_template.ipynb'

    parser.add_argument(
        '--template',
        default=str(default_template),
        help='Template notebook path (default: templates/probability_template.ipynb)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional)'
    )
    parser.add_argument(
        '--name',
        help='Output filename (optional, auto-generated if not provided)'
    )

    args = parser.parse_args()

    # Create generator
    gen = NotebookGenerator(args.bank, seed=args.seed)

    # Filter questions
    try:
        questions = gen.filter_questions(
            args.category,
            args.difficulty
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not questions:
        print("Error: No questions match the criteria")
        sys.exit(1)

    print(f"Found {len(questions)} matching questions")
    print(f"Selecting {min(args.count, len(questions))} for notebook")

    # Create notebook
    diff_str = args.difficulty if args.difficulty else 'mixed'

    nb = gen.create_notebook(
        questions,
        args.count,
        diff_str,
        args.category,
        template_path=args.template
    )

    # Generate output filename
    if args.name:
        filename = args.name
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        cat_str = args.category if args.category else 'mixed'
        filename = f"probability_{cat_str}_{diff_str}_{date_str}.ipynb"

    output_path = Path(args.output) / filename

    # Save notebook
    gen.save_notebook(nb, output_path)

    print(f"\n✓ Generated notebook with {args.count} problems")
    print(f"✓ Category: {args.category or 'mixed'}")
    print(f"✓ Difficulty: {args.difficulty or 'mixed'}")
    print(f"\nOpen with: jupyter notebook {output_path}")


if __name__ == '__main__':
    main()
