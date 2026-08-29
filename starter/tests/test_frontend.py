from pathlib import Path


MAIN_JS = Path(__file__).parents[1] / 'static' / 'main.js'


def test_frontend_locks_clues_and_resets_editable_cells():
    source = MAIN_JS.read_text()

    assert 'inp.disabled = true' in source
    assert "inp.classList.add('prefilled')" in source
    assert "inp.classList.remove('incorrect')" in source
    assert 'renderPuzzle(data.puzzle, data.solution)' in source


def test_frontend_marks_only_wrong_entered_values_invalid():
    source = MAIN_JS.read_text()

    assert "val !== '' && Number(val) !== solution[i][j]" in source
    assert 'e.target.classList.toggle(' in source
    assert "'incorrect'," in source
    assert "e.target.value = val" in source


def test_frontend_displays_completion_message_for_solved_state():
    source = MAIN_JS.read_text()

    assert 'data.solved' in source
    assert "'Congratulations! You solved it!'" in source
    assert "msg.innerText = 'Congratulations! You solved it!'" in source


def test_frontend_implements_timer_reset_and_display():
    source = MAIN_JS.read_text()

    assert 'timerInterval' in source
    assert 'setInterval' in source
    assert 'clearInterval(timerInterval)' in source
    assert 'formatTime' in source
    assert 'timerEl.innerText' in source


def test_frontend_stops_timer_when_board_is_solved():
    source = MAIN_JS.read_text()

    assert 'if (data.solved)' in source
    assert 'stopTimer()' in source
    assert 'clearInterval(timerInterval)' in source


def test_frontend_resets_hint_counter_on_new_game():
    source = MAIN_JS.read_text()

    assert "document.getElementById('hint-count').innerText = 'Hints: 0';" in source
    assert 'currentGameCompleted = false' in source


def test_frontend_blocks_repeat_score_flow_for_solved_game():
    source = MAIN_JS.read_text()

    assert 'currentGameCompleted = true' in source
    assert 'if (currentGameCompleted)' in source
    assert 'if (data.solved)' in source


def test_frontend_timer_element_exists_in_page():
    source = (Path(__file__).parents[1] / 'templates' / 'index.html').read_text()

    assert 'id="timer"' in source
    assert 'Timer:' in source


def test_frontend_implements_scoreboard_storage_and_player_name_flow():
    source = MAIN_JS.read_text()

    assert 'sudokuTopScores' in source
    assert 'player-name' in source
    assert 'Save Score' in source
    assert 'localStorage.getItem' in source
    assert 'localStorage.setItem' in source
    assert 'timeSeconds' in source
    assert 'hintsUsed' in source
    assert 'slice(0, 10)' in source