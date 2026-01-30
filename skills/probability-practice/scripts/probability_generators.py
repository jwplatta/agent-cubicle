"""
Probability problem generators for creating randomized practice problems.

Currently implements:
- JointTableGenerator: Creates 2×2 contingency tables with random integer counts
"""

import random
from typing import Dict, List, Tuple
from fraction_utils import simplify_fraction, format_probability


class JointTableGenerator:
    """
    Generate 2×2 contingency tables with random integer counts.

    The tables follow this structure:
                 B      ¬B    Total
        A        a      b     a+b
        ¬A       c      d     c+d
        Total   a+c    b+d     N

    All generated tables have:
    - Positive counts in all cells (no zeros)
    - Specified total count N
    - Optional adjustment for simple fractions
    """

    def __init__(self, seed=None):
        """
        Initialize generator with optional random seed.

        Args:
            seed: Random seed for reproducibility (optional)
        """
        if seed is not None:
            random.seed(seed)

    def generate_2x2(
        self,
        total: int = 20,
        ensure_simple_fractions: bool = True
    ) -> Dict:
        """
        Generate a random 2×2 contingency table.

        Args:
            total: Total count N (default: 20)
            ensure_simple_fractions: If True, adjust counts to avoid ugly fractions

        Returns:
            Dictionary with:
            - a, b, c, d: Cell counts (integers)
            - total: N
            - table_str: Formatted markdown table
            - marginal_A: P(A) count (a+b)
            - marginal_B: P(B) count (a+c)
            - marginal_notA: P(¬A) count (c+d)
            - marginal_notB: P(¬B) count (b+d)
            - joint_AB: P(A∩B) count (a)
            - joint_A_notB: P(A∩¬B) count (b)
            - joint_notA_B: P(¬A∩B) count (c)
            - joint_notA_notB: P(¬A∩¬B) count (d)

        Example:
            >>> gen = JointTableGenerator(seed=42)
            >>> table = gen.generate_2x2(total=20)
            >>> print(table['table_str'])
                       B      ¬B    Total
            A          6      4       10
            ¬A         3      7       10
            Total      9     11       20
        """
        # Generate random counts that sum to total
        # Ensure all cells have at least 1 count
        if total < 4:
            raise ValueError("Total must be at least 4 to ensure all cells > 0")

        # Use Dirichlet-like approach: randomly split total into 4 parts
        # ensuring each part is at least 1
        remaining = total - 4  # Reserve 1 for each cell
        splits = sorted([0, random.randint(1, remaining), random.randint(1, remaining), remaining])

        a = splits[1] - splits[0] + 1
        b = splits[2] - splits[1] + 1
        c = splits[3] - splits[2] + 1
        d = remaining - splits[3] + 1

        # Verify sum
        assert a + b + c + d == total, f"Sum mismatch: {a}+{b}+{c}+{d} != {total}"
        assert all(x > 0 for x in [a, b, c, d]), f"Zero cell: {a}, {b}, {c}, {d}"

        # Optional: adjust for simple fractions
        if ensure_simple_fractions:
            a, b, c, d = self._adjust_for_simple_fractions(a, b, c, d, total)

        # Calculate marginals
        marginal_A = a + b
        marginal_notA = c + d
        marginal_B = a + c
        marginal_notB = b + d

        # Format table
        table_str = self._format_table(a, b, c, d)

        return {
            'a': a,
            'b': b,
            'c': c,
            'd': d,
            'total': total,
            'table_str': table_str,
            'marginal_A': marginal_A,
            'marginal_notA': marginal_notA,
            'marginal_B': marginal_B,
            'marginal_notB': marginal_notB,
            'joint_AB': a,
            'joint_A_notB': b,
            'joint_notA_B': c,
            'joint_notA_notB': d,
        }

    def _format_table(self, a: int, b: int, c: int, d: int) -> str:
        """
        Return markdown-formatted table string.

        Args:
            a, b, c, d: Cell counts

        Returns:
            Markdown table string
        """
        marginal_A = a + b
        marginal_notA = c + d
        marginal_B = a + c
        marginal_notB = b + d
        total = a + b + c + d

        # Use fixed-width formatting for alignment
        table = f"""
|        | B      | ¬B     | Total  |
|--------|--------|--------|--------|
| **A**  | {a:>6} | {b:>6} | {marginal_A:>6} |
| **¬A** | {c:>6} | {d:>6} | {marginal_notA:>6} |
| **Total** | {marginal_B:>6} | {marginal_notB:>6} | {total:>6} |
"""
        return table.strip()

    def _adjust_for_simple_fractions(
        self,
        a: int,
        b: int,
        c: int,
        d: int,
        total: int
    ) -> Tuple[int, int, int, int]:
        """
        Adjust counts to produce cleaner fractions when possible.

        Strategy: If total has nice divisors (2, 3, 4, 5, etc.),
        try to make marginals be multiples of those divisors.

        Args:
            a, b, c, d: Original cell counts
            total: Total count

        Returns:
            Adjusted (a, b, c, d) tuple
        """
        # For now, use a simple heuristic: if total is divisible by small numbers,
        # try to make marginals divisible too
        nice_divisors = [2, 3, 4, 5, 6, 8, 10]
        applicable_divisors = [div for div in nice_divisors if total % div == 0]

        if not applicable_divisors:
            return (a, b, c, d)

        # Try to adjust marginal_A to be a multiple of a nice divisor
        target_div = random.choice(applicable_divisors)
        marginal_A = a + b

        # Find nearest multiple of target_div
        new_marginal_A = round(marginal_A / target_div) * target_div
        new_marginal_A = max(2, min(total - 2, new_marginal_A))  # Keep in valid range

        # Adjust a and b proportionally
        if marginal_A != new_marginal_A:
            ratio = new_marginal_A / marginal_A
            new_a = max(1, round(a * ratio))
            new_b = max(1, new_marginal_A - new_a)

            # Adjust c and d to maintain total
            new_marginal_notA = total - new_marginal_A
            marginal_B = a + c
            new_c = max(1, min(new_marginal_notA - 1, marginal_B - new_a))
            new_d = new_marginal_notA - new_c

            # Verify validity
            if all(x > 0 for x in [new_a, new_b, new_c, new_d]):
                if new_a + new_b + new_c + new_d == total:
                    return (new_a, new_b, new_c, new_d)

        # If adjustment failed, return original
        return (a, b, c, d)

    def generate_with_scenario(
        self,
        total: int = 20,
        scenario: str = "abstract"
    ) -> Dict:
        """
        Generate table with optional real-world scenario wrapping.

        Args:
            total: Total count
            scenario: One of "abstract", "medical", "quality", "survey"

        Returns:
            Same as generate_2x2() but with scenario-specific labels
        """
        table = self.generate_2x2(total=total)

        scenarios = {
            "abstract": ("Event A", "Event B"),
            "medical": ("Disease", "Test Positive"),
            "quality": ("Defective", "From Supplier A"),
            "survey": ("Satisfied", "Premium Customer")
        }

        if scenario not in scenarios:
            scenario = "abstract"

        label_A, label_B = scenarios[scenario]
        table['label_A'] = label_A
        table['label_B'] = label_B
        table['scenario'] = scenario

        return table
