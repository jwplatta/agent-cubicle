#!/usr/bin/env python3
"""
Randomly select and enrich probability questions from question banks.

Usage:
    python question_randomizer.py --topics combinations permutations --count 10
    python question_randomizer.py --topics combinations --count 5 --seed 42
    python question_randomizer.py --topics permutations --count 8 --output selected.json
"""

import argparse
import json
import random
import sys
from pathlib import Path
from enrich_question import enrich_question


def load_question_bank(topic):
    """
    Load questions from a topic's JSON file.

    Args:
        topic: Topic name (e.g., 'combinations', 'permutations')

    Returns:
        List of question dictionaries

    Raises:
        FileNotFoundError: If question file doesn't exist
        ValueError: If JSON structure is unexpected
    """
    # Navigate to questions directory from scripts directory
    questions_dir = Path(__file__).parent.parent / 'questions'
    question_file = questions_dir / f'{topic}.json'

    if not question_file.exists():
        raise FileNotFoundError(f"Question bank not found: {question_file}")

    with open(question_file, 'r') as f:
        data = json.load(f)

    if "questions" not in data:
        raise ValueError(f"Expected key 'questions' in {question_file}")

    return data["questions"]

def select_questions(topics, count, max_difficulty=None, seed=None):
    """
    Select questions proportionally from each topic and enrich them.

    Args:
        topics: List of topic names (e.g., ['combinations', 'permutations'])
        count: Total number of questions to select
        max_difficulty: Maximum difficulty level (for future filtering)
        seed: Random seed for reproducibility

    Returns:
        List of dictionaries with enriched questions, each containing:
            - question: Enriched question text
            - solution: Solution description (or empty string)
            - difficulty: Difficulty level (or empty string)
            - topic: Topic name
    """
    if seed is not None:
        random.seed(seed)

    # Load all questions from each topic
    all_questions = {}
    for topic in topics:
        try:
            all_questions[topic] = load_question_bank(topic)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Calculate how many questions to select from each topic (proportional distribution)
    questions_per_topic = count // len(topics)
    remainder = count % len(topics)

    selected = []

    for i, topic in enumerate(topics):
        # Distribute remainder among first few topics
        topic_count = questions_per_topic + (1 if i < remainder else 0)

        # Get available questions for this topic
        available = all_questions[topic]

        # Filter by difficulty if specified (not implemented yet, placeholder)
        # if max_difficulty:
        #     available = filter_by_difficulty(available, max_difficulty)

        # Sample from available questions
        if len(available) < topic_count:
            print(
                f"Warning: Only {len(available)} questions available for '{topic}', "
                f"requested {topic_count}",
                file=sys.stderr
            )
            sampled = available
        else:
            sampled = random.sample(available, topic_count)

        # Enrich each question and add metadata
        for q in sampled:
            # Enrich the question text by replacing placeholders
            enriched_text = enrich_question(q['question'], seed=None)

            selected.append({
                'question': enriched_text,
                'solution': q.get('solution', ''),
                'difficulty': q.get('difficulty', ''),
                'topic': topic
            })

    # Shuffle the final list so topics are mixed together
    random.shuffle(selected)

    return selected


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Randomly select and enrich probability questions from topic banks"
    )
    parser.add_argument(
        '--topics',
        nargs='+',
        required=True,
        help='Topic names (e.g., combinations permutations)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Total number of questions to select (default: 10)'
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        help='Maximum difficulty level (optional, not yet implemented)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility (optional)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (optional, prints to stdout if not provided)'
    )

    args = parser.parse_args()

    questions = select_questions(
        topics=args.topics,
        count=args.count,
        max_difficulty=args.difficulty,
        seed=args.seed
    )

    output = json.dumps(questions, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(output)
        print(f"Wrote {len(questions)} questions to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
