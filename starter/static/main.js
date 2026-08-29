// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const STORAGE_KEY = 'sudokuTopScores';
const MAX_SCORE_ENTRIES = 10;
let puzzle = [];
let solution = [];
let timerInterval = null;
let startTime = null;
let currentDifficulty = 'Medium';
let currentGameCompleted = false;

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  if (!timerEl) return;
  const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
  timerEl.innerText = `Timer: ${formatTime(elapsedSeconds)}`;
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  startTime = Date.now();
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    updateTimerDisplay();
  }, 1000);
}

function getElapsedSeconds() {
  if (!startTime) return 0;
  return Math.floor((Date.now() - startTime) / 1000);
}

function getCurrentHintCount() {
  const hintText = document.getElementById('hint-count').innerText;
  const match = hintText.match(/(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
}

function readScores() {
  try {
    const rawScores = localStorage.getItem(STORAGE_KEY);
    if (!rawScores) {
      return [];
    }
    const parsedScores = JSON.parse(rawScores);
    if (!Array.isArray(parsedScores)) {
      return [];
    }
    return parsedScores.filter((score) => {
      return score
        && typeof score.playerName === 'string'
        && score.playerName.trim() !== ''
        && typeof score.timeSeconds === 'number'
        && typeof score.difficulty === 'string'
        && typeof score.hintsUsed === 'number';
    });
  } catch (error) {
    return [];
  }
}

function sortScores(scores) {
  const sortedScores = [...scores].sort((a, b) => {
    if (a.timeSeconds !== b.timeSeconds) {
      return a.timeSeconds - b.timeSeconds;
    }
    if (a.hintsUsed !== b.hintsUsed) {
      return a.hintsUsed - b.hintsUsed;
    }
    return a.playerName.localeCompare(b.playerName);
  });
  return sortedScores.slice(0, 10);
}

function renderScoreboard() {
  const listEl = document.getElementById('scoreboard-list');
  if (!listEl) return;

  const scores = sortScores(readScores());
  listEl.innerHTML = '';

  if (scores.length === 0) {
    const item = document.createElement('li');
    item.textContent = 'No scores yet';
    listEl.appendChild(item);
    return;
  }

  scores.forEach((score, index) => {
    const item = document.createElement('li');
    item.textContent = `${index + 1}. ${score.playerName} — ${formatTime(score.timeSeconds)} — ${score.difficulty} — ${score.hintsUsed} hints`;
    listEl.appendChild(item);
  });
}

function hideScoreEntryForm() {
  const form = document.getElementById('score-entry-form');
  if (!form) return;
  form.hidden = true;
  document.getElementById('player-name').value = '';
}

function showScoreEntryForm() {
  const form = document.getElementById('score-entry-form');
  if (!form) return;
  form.hidden = false;
  const saveButton = document.getElementById('save-score');
  if (saveButton) {
    saveButton.textContent = 'Save Score';
  }
  document.getElementById('player-name').focus();
}

function saveScore() {
  const input = document.getElementById('player-name');
  const msg = document.getElementById('message');
  const playerName = input.value.trim();

  if (!playerName) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Enter a player name before saving your score.';
    return;
  }

  const currentScore = {
    playerName,
    timeSeconds: getElapsedSeconds(),
    difficulty: currentDifficulty,
    hintsUsed: getCurrentHintCount(),
  };

  const scores = sortScores([...readScores(), currentScore]);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
  renderScoreboard();
  hideScoreEntryForm();
  msg.style.color = '#388e3c';
  msg.innerText = 'Score saved!';
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        e.target.classList.toggle(
          'incorrect',
          val !== '' && Number(val) !== solution[i][j],
        );
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, sol) {
  puzzle = puz;
  solution = sol;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.classList.remove('incorrect');
      }
    }
  }
}

async function newGame() {
  currentDifficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(currentDifficulty)}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  currentGameCompleted = false;
  document.getElementById('hint-count').innerText = 'Hints: 0';
  renderPuzzle(data.puzzle, data.solution);
  document.getElementById('message').innerText = '';
  hideScoreEntryForm();
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (data.solved) {
    if (currentGameCompleted) {
      return;
    }
    currentGameCompleted = true;
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    showScoreEntryForm();
    return;
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = '';
    return;
  }
  msg.style.color = '#d32f2f';
  msg.innerText = 'Some cells are incorrect.';
}

async function requestHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  // Build current board state
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  // Request hint from backend
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();

  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  // Fill the hinted cell and lock it
  const hintedIndex = data.row * SIZE + data.col;
  const hintedInput = inputs[hintedIndex];
  hintedInput.value = data.value;
  hintedInput.disabled = true;
  hintedInput.classList.add('prefilled');

  // Update hint count display
  document.getElementById('hint-count').innerText = 'Hints: ' + data.hint_count;
  msg.innerText = '';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('save-score').addEventListener('click', saveScore);
  renderScoreboard();
  // initialize
  newGame();
});
