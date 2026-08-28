import copy
import random

SIZE = 9
EMPTY = 0
MIN_UNIQUE_CLUES = 17
DIFFICULTY_CLUES = {
    "Easy": 45,
    "Medium": 35,
    "Hard": 25,
}
DEFAULT_DIFFICULTY = "Medium"

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Return the number of solutions, stopping once ``limit`` is reached."""
    if limit < 1:
        return 0
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return 0
    if any(
        value not in range(0, SIZE + 1)
        for row in board
        for value in row
    ):
        return 0

    working_board = deep_copy(board)

    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if value == EMPTY:
                continue
            working_board[row][col] = EMPTY
            if not is_safe(working_board, row, col, value):
                return 0
            working_board[row][col] = value

    def count_from_board():
        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue

                candidates = [
                    value
                    for value in range(1, SIZE + 1)
                    if is_safe(working_board, row, col, value)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

        if best_cell is None:
            return 1

        row, col = best_cell
        solution_count = 0
        for candidate in best_candidates:
            working_board[row][col] = candidate
            solution_count += count_from_board()
            working_board[row][col] = EMPTY
            if solution_count >= limit:
                return limit
        return solution_count

    return count_from_board()

def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1

def generate_puzzle(clues=35):
    if not isinstance(clues, int) or isinstance(clues, bool):
        raise ValueError("clues must be an integer")
    if clues < MIN_UNIQUE_CLUES or clues > SIZE * SIZE:
        raise ValueError(
            f"clues must be between {MIN_UNIQUE_CLUES} and {SIZE * SIZE}"
        )

    for _ in range(100):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
        random.shuffle(cells)

        for row, col in cells:
            if sum(cell != EMPTY for row in board for cell in row) == clues:
                return deep_copy(board), solution

            value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board) != 1:
                board[row][col] = value

        if sum(cell != EMPTY for row in board for cell in row) == clues:
            return deep_copy(board), solution

    raise RuntimeError("Unable to generate a uniquely solvable puzzle")


def generate_puzzle_for_difficulty(difficulty=DEFAULT_DIFFICULTY):
    """Generate a uniquely solvable puzzle for a named difficulty level."""
    if difficulty not in DIFFICULTY_CLUES:
        raise ValueError("difficulty must be Easy, Medium, or Hard")
    return generate_puzzle(clues=DIFFICULTY_CLUES[difficulty])
