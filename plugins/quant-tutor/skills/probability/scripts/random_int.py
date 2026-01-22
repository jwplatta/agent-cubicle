import random
import sys

def random_int(min_val, max_val):
    """
    Returns a random integer between min_val and max_val (inclusive).
    """
    return random.randint(min_val, max_val)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python random_int.py <min> <max>")
        sys.exit(1)

    min_val = int(sys.argv[1])
    max_val = int(sys.argv[2])
    print(random_int(min_val, max_val))