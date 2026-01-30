"""
Fraction utility functions for probability problems.

Provides functions for simplifying fractions, formatting probabilities,
and checking user answers against correct solutions.
"""

from math import gcd
from fractions import Fraction


def simplify_fraction(num, denom):
    """
    Reduce fraction to simplest form.

    Args:
        num: Numerator (int)
        denom: Denominator (int)

    Returns:
        Tuple of (numerator, denominator) in simplest form

    Examples:
        >>> simplify_fraction(4, 8)
        (1, 2)
        >>> simplify_fraction(15, 20)
        (3, 4)
    """
    if denom == 0:
        raise ValueError("Denominator cannot be zero")

    common = gcd(abs(num), abs(denom))
    return (num // common, denom // common)


def format_probability(num, denom):
    """
    Format probability as 'a/b = 0.xxxx' or just 'a' if denominator is 1.

    Args:
        num: Numerator (int)
        denom: Denominator (int)

    Returns:
        Formatted string representation

    Examples:
        >>> format_probability(3, 4)
        '3/4 = 0.7500'
        >>> format_probability(5, 1)
        '5'
        >>> format_probability(1, 3)
        '1/3 = 0.3333'
    """
    simple_num, simple_denom = simplify_fraction(num, denom)

    if simple_denom == 1:
        return str(simple_num)

    decimal_value = simple_num / simple_denom
    return f"{simple_num}/{simple_denom} = {decimal_value:.4f}"


def check_probability(user_answer, correct_num, correct_denom):
    """
    Helper function for notebook - checks if user's answer matches.

    This function is designed to be copied into generated notebooks
    for students to verify their answers.

    Args:
        user_answer: User's answer (can be string like "3/4", float, or Fraction)
        correct_num: Correct numerator (int)
        correct_denom: Correct denominator (int)

    Returns:
        Boolean indicating if answer is correct

    Examples:
        >>> check_probability("3/4", 3, 4)
        ✓ Correct! 3/4 = 0.7500
        True
        >>> check_probability(0.75, 3, 4)
        ✓ Correct! 3/4 = 0.7500
        True
        >>> check_probability("1/2", 3, 4)
        ✗ Your answer: 1/2 = 0.5000
          Correct: 3/4 = 0.7500
        False
    """
    correct = Fraction(correct_num, correct_denom)

    # Convert user answer to Fraction
    if isinstance(user_answer, str):
        try:
            yours = Fraction(user_answer).limit_denominator()
        except (ValueError, ZeroDivisionError):
            print(f"✗ Invalid format: {user_answer}")
            print(f"  Expected format: '3/4' or 0.75")
            return False
    elif isinstance(user_answer, (int, float)):
        yours = Fraction(user_answer).limit_denominator()
    elif isinstance(user_answer, Fraction):
        yours = user_answer
    else:
        print(f"✗ Invalid type: {type(user_answer)}")
        print(f"  Expected: string ('3/4'), float (0.75), or Fraction")
        return False

    # Compare
    if yours == correct:
        print(f"✓ Correct! {yours} = {float(yours):.4f}")
        return True
    else:
        print(f"✗ Your answer: {yours} = {float(yours):.4f}")
        print(f"  Correct: {correct} = {float(correct):.4f}")
        return False
