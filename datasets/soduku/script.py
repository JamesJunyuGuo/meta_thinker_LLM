import numpy as np
quizzes = np.load('sudoku_quizzes.npy') # shape = (1000000, 9, 9)
solutions = np.load('sudoku_solutions.npy') # shape = (1000000, 9, 9)
for quiz, solution in zip(quizzes[:10], solutions[:10]):
    print(quiz)
    print(solution)