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