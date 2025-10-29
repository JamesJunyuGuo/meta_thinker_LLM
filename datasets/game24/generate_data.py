import random
import csv
from fractions import Fraction

def find_solution(nums_expr):
    """
    Recursive function that tries to combine numbers (with +, -, *, /)
    to reach 24. Each element in nums_expr is a tuple (value, expression).
    """
    if len(nums_expr) == 1:
        # Check if we've reached 24 exactly.
        if nums_expr[0][0] == Fraction(24, 1):
            return nums_expr[0][1]
        return None

    # Try every pair of numbers.
    for i in range(len(nums_expr)):
        for j in range(i + 1, len(nums_expr)):
            a, expr_a = nums_expr[i]
            b, expr_b = nums_expr[j]
            # The remaining numbers (not used in this operation)
            next_nums = [nums_expr[k] for k in range(len(nums_expr)) if k not in (i, j)]
            
            # List all possible operations (note that subtraction and division are not commutative).
            possibilities = []
            possibilities.append((a + b, f"({expr_a}+{expr_b})"))
            possibilities.append((a - b, f"({expr_a}-{expr_b})"))
            possibilities.append((b - a, f"({expr_b}-{expr_a})"))
            possibilities.append((a * b, f"({expr_a}*{expr_b})"))
            if b != 0:
                possibilities.append((a / b, f"({expr_a}/{expr_b})"))
            if a != 0:
                possibilities.append((b / a, f"({expr_b}/{expr_a})"))
            
            # Recurse with each new possibility.
            for val, expr in possibilities:
                result = find_solution(next_nums + [(val, expr)])
                if result is not None:
                    return result
    return None

def solve_puzzle(numbers):
    """
    Given a list of 5 integers, return a valid arithmetic expression string that evaluates to 24,
    or None if no solution is found.
    """
    nums_expr = [(Fraction(n, 1), str(n)) for n in numbers]
    return find_solution(nums_expr)

def generate_dataset(num_puzzles=900):
    """
    Generates a list of puzzles. Each puzzle is represented as a dictionary with:
    - id: sequential id,
    - num1, num2, num3, num4, num5: the five numbers,
    - solution: a string showing one arithmetic expression that yields 24.
    
    To encourage variety, puzzles are kept unique based on their sorted number tuple.
    """
    dataset = []
    unique_set = set()
    attempts = 0

    while len(dataset) < num_puzzles:
        attempts += 1
        # Generate 5 random numbers in the range 1 to 10.
        puzzle = [random.randint(1, 10) for _ in range(5)]
        # Use sorted tuple for uniqueness.
        puzzle_key = tuple(sorted(puzzle))
        if puzzle_key in unique_set:
            continue

        solution = solve_puzzle(puzzle)
        if solution is not None:
            dataset.append({
                "id": len(dataset) + 1,
                "num1": puzzle[0],
                "num2": puzzle[1],
                "num3": puzzle[2],
                "num4": puzzle[3],
                "num5": puzzle[4],
                "solution": solution + " = 24"
            })
            unique_set.add(puzzle_key)
    
    print("Total attempts to generate 900 puzzles:", attempts)
    return dataset

def save_to_csv(dataset, filename="24game_900.csv"):
    """
    Saves the dataset to a CSV file with headers: id, num1, num2, num3, num4, num5, solution.
    """
    with open(filename, mode="w", newline="") as csvfile:
        fieldnames = ["id", "num1", "num2", "num3", "num4", "num5", "solution"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in dataset:
            writer.writerow(row)

if __name__ == "__main__":
    dataset = generate_dataset(900)
    save_to_csv(dataset)
    print("Dataset saved to 24game_900.csv")
