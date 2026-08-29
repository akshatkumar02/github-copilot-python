import random

import sudoku_logic


def assert_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected for row in board)
    assert all(
        {board[row][col] for row in range(sudoku_logic.SIZE)} == expected
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row][col]
            for row in range(box_row, box_row + 3)
            for col in range(box_col, box_col + 3)
        }
        == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )


def test_create_empty_board_has_nine_rows_of_zeroes():
    board = sudoku_logic.create_empty_board()

    assert board == [[0] * 9 for _ in range(9)]


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert sudoku_logic.is_safe(board, 0, 1, 1) is False
    assert sudoku_logic.is_safe(board, 1, 0, 1) is False
    assert sudoku_logic.is_safe(board, 1, 1, 1) is False
    assert sudoku_logic.is_safe(board, 1, 1, 2) is True


def test_fill_board_creates_a_valid_solution():
    random.seed(0)
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert_valid_solution(board)


def test_generate_puzzle_returns_solution_and_requested_number_of_clues():
    random.seed(0)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert_valid_solution(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_generated_puzzle_has_exactly_one_solution():
    random.seed(0)

    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(puzzle) == 1


def test_difficulty_levels_have_ordered_unique_clue_counts_and_solutions():
    clue_counts = {}

    for difficulty in ("Easy", "Medium", "Hard"):
        random.seed(0)
        puzzle, _ = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        clue_counts[difficulty] = sum(
            cell != sudoku_logic.EMPTY for row in puzzle for cell in row
        )
        assert sudoku_logic.count_solutions(puzzle) == 1

    assert clue_counts == {"Easy": 45, "Medium": 35, "Hard": 25}
    assert clue_counts["Easy"] > clue_counts["Medium"] > clue_counts["Hard"]


def test_generate_puzzle_for_difficulty_rejects_invalid_values():
    for difficulty in ("", "Extreme", None, 1):
        try:
            sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid difficulty was accepted")


def test_returned_solution_solves_generated_puzzle():
    random.seed(1)

    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.count_solutions(solution) == 1


def test_count_solutions_returns_zero_for_an_invalid_board():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1

    assert sudoku_logic.count_solutions(board) == 0
    assert sudoku_logic.count_solutions([[10] * 9 for _ in range(9)]) == 0


def test_get_hint_returns_first_empty_cell_with_correct_value():
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1

    hint = sudoku_logic.get_hint(board, solution)

    assert hint is not None
    assert hint[0] == 0
    assert hint[1] == 1
    assert hint[2] == 2


def test_get_hint_returns_none_when_board_is_complete():
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    board = [row[:] for row in solution]

    hint = sudoku_logic.get_hint(board, solution)

    assert hint is None


def test_get_hint_skips_filled_cells():
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    board[0][1] = 2
    board[0][2] = 3

    hint = sudoku_logic.get_hint(board, solution)

    assert hint is not None
    assert hint[0] == 0
    assert hint[1] == 3
    assert hint[2] == 4


def test_get_hint_works_with_different_puzzle_states():
    solution = [[1] * 9 for _ in range(9)]
    solution[5][5] = 5

    # Partially filled board
    board = [[0] * 9 for _ in range(9)]
    board[3][3] = 1

    hint = sudoku_logic.get_hint(board, solution)

    assert hint == (0, 0, 1)

    # Update board with hint
    board[0][0] = 1

    hint2 = sudoku_logic.get_hint(board, solution)

    assert hint2 == (0, 1, 1)
    assert hint != hint2