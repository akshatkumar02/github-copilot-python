from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hint_count': 0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    if difficulty is None:
        if 'clues' in request.args:
            clues = int(request.args['clues'])
            puzzle, solution = sudoku_logic.generate_puzzle(clues)
            CURRENT['puzzle'] = puzzle
            CURRENT['solution'] = solution
            CURRENT['hint_count'] = 0
            CURRENT.pop('difficulty', None)
            return jsonify({'puzzle': puzzle, 'solution': solution})
        difficulty = sudoku_logic.DEFAULT_DIFFICULTY
    if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
        return jsonify({'error': 'Invalid difficulty'}), 400

    puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['hint_count'] = 0
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    solved = all(cell != sudoku_logic.EMPTY for row in board for cell in row) and not incorrect
    return jsonify({'incorrect': incorrect, 'solved': solved})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    hint_data = sudoku_logic.get_hint(board, solution)
    if hint_data is None:
        return jsonify({'error': 'No empty cells available'}), 400

    CURRENT['hint_count'] += 1
    row, col, value = hint_data
    return jsonify({'row': row, 'col': col, 'value': value, 'hint_count': CURRENT['hint_count']})

if __name__ == '__main__':
    app.run(debug=True)
