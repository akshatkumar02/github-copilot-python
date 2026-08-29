import app as app_module


def test_index_renders_game_controls(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'<select id="difficulty">' in response.data
    assert b'New Game' in response.data
    assert b'Check Solution' in response.data


def test_new_game_uses_requested_clues_and_returns_puzzle(client, monkeypatch):
    puzzle = [[0] * 9 for _ in range(9)]
    solution = [[1] * 9 for _ in range(9)]
    received = {}

    def fake_generate_puzzle(clues):
        received['clues'] = clues
        return puzzle, solution

    monkeypatch.setattr(app_module.sudoku_logic, 'generate_puzzle', fake_generate_puzzle)

    response = client.get('/new?clues=40')

    assert response.status_code == 200
    assert response.get_json() == {'puzzle': puzzle, 'solution': solution}
    assert received['clues'] == 40
    assert app_module.CURRENT == {'puzzle': puzzle, 'solution': solution}


def test_new_game_defaults_to_medium(client, monkeypatch):
    received = {}

    def fake_generate_puzzle(difficulty):
        received['difficulty'] = difficulty
        return [[0] * 9 for _ in range(9)], [[1] * 9 for _ in range(9)]

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        fake_generate_puzzle,
    )

    response = client.get('/new')

    assert response.status_code == 200
    assert received['difficulty'] == 'Medium'
    assert app_module.CURRENT['difficulty'] == 'Medium'


def test_new_game_accepts_each_difficulty(client, monkeypatch):
    received = []

    def fake_generate_puzzle(difficulty):
        received.append(difficulty)
        return [[0] * 9 for _ in range(9)], [[1] * 9 for _ in range(9)]

    monkeypatch.setattr(
        app_module.sudoku_logic,
        'generate_puzzle_for_difficulty',
        fake_generate_puzzle,
    )

    for difficulty in ('Easy', 'Medium', 'Hard'):
        response = client.get(f'/new?difficulty={difficulty}')
        assert response.status_code == 200
        assert response.get_json()['difficulty'] == difficulty
        assert response.get_json()['solution'] == [[1] * 9 for _ in range(9)]

    assert received == ['Easy', 'Medium', 'Hard']


def test_new_game_rejects_invalid_difficulty(client):
    response = client.get('/new?difficulty=Extreme')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid difficulty'}


def test_check_solution_requires_a_game(client):
    app_module.CURRENT.update(puzzle=None, solution=None)

    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_solution_reports_cells_that_differ(client):
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    app_module.CURRENT.update(puzzle=solution, solution=solution)
    board = [row[:] for row in solution]
    board[0][0] = 0
    board[8][8] = 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0], [8, 8]], 'solved': False}


def test_check_solution_reports_complete_board_as_solved(client):
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    app_module.CURRENT.update(puzzle=solution, solution=solution)

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'solved': True}


def test_check_solution_reports_incomplete_board_as_unsolved(client):
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    board = [row[:] for row in solution]
    board[0][0] = 0
    app_module.CURRENT.update(puzzle=solution, solution=solution)

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['solved'] is False
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_check_solution_reports_incorrect_board_as_unsolved(client):
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board = [row[:] for row in solution]
    board[8][8] = 1
    app_module.CURRENT.update(puzzle=solution, solution=solution)

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['solved'] is False
    assert response.get_json()['incorrect'] == [[8, 8]]


def test_check_solution_accepts_a_matching_board(client):
    solution = [[value for value in range(1, 10)] for _ in range(9)]
    app_module.CURRENT.update(puzzle=solution, solution=solution)

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [], 'solved': True}