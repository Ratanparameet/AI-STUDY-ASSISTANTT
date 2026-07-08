// ===========================================================
// MCQ Quiz Engine — Timer, Navigation, Submit, Results, Review
// ===========================================================
let mcqQuestions = [];
let mcqAnswers = {};
let currentQIndex = 0;
let mcqTestId = null;
let mcqSubject = '';
let timerInterval = null;
let totalSeconds = 20 * 60; // 20 minutes
let startTime = null;

document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('start-mcq-btn');
  if (startBtn) startBtn.addEventListener('click', startMcqTest);

  const prevBtn = document.getElementById('quiz-prev-btn');
  const nextBtn = document.getElementById('quiz-next-btn');
  const submitBtn = document.getElementById('quiz-submit-btn');

  if (prevBtn) prevBtn.addEventListener('click', () => navigateQuestion(-1));
  if (nextBtn) nextBtn.addEventListener('click', () => navigateQuestion(1));
  if (submitBtn) submitBtn.addEventListener('click', submitMcqTest);
});

async function startMcqTest() {
  const subjectSelect = document.getElementById('mcq-subject-select');
  mcqSubject = subjectSelect ? subjectSelect.value : 'Embedded Systems';

  const typeSelect = document.getElementById('mcq-type-select');
  const mcqType = typeSelect ? typeSelect.value : 'Full Syllabus Mock Test';

  showLoading('Generating MCQ test...');

  try {
    const res = await Auth.fetchWithAuth('/generate-mcq', {
      method: 'POST',
      headers: Auth.getHeaders(),
      body: JSON.stringify({ subject: mcqSubject, exam_type: mcqType })
    });

    hideLoading();
    if (!res) return;
    const data = await res.json();
    if (!res.ok) { showToast(data.detail || 'Failed to generate MCQs', 'error'); return; }

    mcqQuestions = data.questions || [];
    mcqTestId = data.test_id;
    mcqAnswers = {};
    currentQIndex = 0;
    totalSeconds = mcqQuestions.length * 60; // 1 minute per question (dynamic)
    startTime = Date.now();

    if (mcqQuestions.length === 0) {
      showToast('No questions available for this subject', 'warning');
      return;
    }

    // Switch to quiz screen
    document.getElementById('mcq-start-screen').style.display = 'none';
    document.getElementById('mcq-quiz-screen').style.display = 'block';
    document.getElementById('mcq-result-screen').style.display = 'none';

    renderQuestion();
    startTimer();
    showToast(`Test started! ${mcqQuestions.length} questions • 20 min`, 'info');
  } catch (err) {
    hideLoading();
    showToast('Failed to start test', 'error');
    console.error(err);
  }
}

function renderQuestion() {
  const q = mcqQuestions[currentQIndex];
  if (!q) return;

  const total = mcqQuestions.length;

  // Question number
  document.getElementById('quiz-q-number').textContent = `Question ${currentQIndex + 1} of ${total}`;

  // Progress
  const pct = ((currentQIndex + 1) / total) * 100;
  document.getElementById('quiz-progress-fill').style.width = pct + '%';

  // Badges
  document.getElementById('quiz-badges').innerHTML = `
    ${priorityBadge(q.priority)}
    ${difficultyBadge(q.difficulty)}
  `;

  // Question text
  document.getElementById('quiz-question-text').textContent = q.question;

  // Options
  const optionsDiv = document.getElementById('quiz-options');
  const selectedAnswer = mcqAnswers[q.id] || '';

  optionsDiv.innerHTML = q.options.map(opt => {
    const letter = opt.trim().charAt(0);
    const isSelected = selectedAnswer === letter;
    return `
      <div class="quiz-option ${isSelected ? 'selected' : ''}" data-letter="${letter}" onclick="selectOption('${q.id}', '${letter}', this)">
        <div class="option-letter">${letter}</div>
        <div class="option-text">${escapeHtml(opt)}</div>
      </div>`;
  }).join('');

  // Nav buttons
  document.getElementById('quiz-prev-btn').disabled = currentQIndex === 0;
  
  if (currentQIndex === total - 1) {
    document.getElementById('quiz-next-btn').style.display = 'none';
    document.getElementById('quiz-submit-btn').style.display = 'inline-flex';
  } else {
    document.getElementById('quiz-next-btn').style.display = 'inline-flex';
    document.getElementById('quiz-submit-btn').style.display = 'none';
  }
}

function selectOption(questionId, letter, element) {
  mcqAnswers[questionId] = letter;

  // Update UI
  const parent = element.parentElement;
  parent.querySelectorAll('.quiz-option').forEach(opt => opt.classList.remove('selected'));
  element.classList.add('selected');
}

function navigateQuestion(direction) {
  const newIndex = currentQIndex + direction;
  if (newIndex >= 0 && newIndex < mcqQuestions.length) {
    currentQIndex = newIndex;
    renderQuestion();
  }
}

function startTimer() {
  if (timerInterval) clearInterval(timerInterval);
  const display = document.getElementById('timer-display');
  const timerContainer = document.getElementById('quiz-timer');

  timerInterval = setInterval(() => {
    totalSeconds--;
    if (totalSeconds <= 0) {
      clearInterval(timerInterval);
      showToast('Time is up! Submitting test...', 'warning');
      submitMcqTest();
      return;
    }

    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    timerContainer.classList.remove('warning', 'danger');
    if (totalSeconds <= 60) timerContainer.classList.add('danger');
    else if (totalSeconds <= 180) timerContainer.classList.add('warning');
  }, 1000);
}

async function submitMcqTest() {
  if (timerInterval) clearInterval(timerInterval);
  const timeTaken = Math.floor((Date.now() - startTime) / 1000);

  // Build answers array
  const answersArr = mcqQuestions.map(q => ({
    question_id: q.id,
    selected_option: mcqAnswers[q.id] || ''
  }));

  showLoading('Grading your test...');

  try {
    const res = await Auth.fetchWithAuth('/submit-test', {
      method: 'POST',
      headers: Auth.getHeaders(),
      body: JSON.stringify({
        test_id: mcqTestId,
        subject: mcqSubject,
        answers: answersArr,
        time_taken: timeTaken
      })
    });

    hideLoading();
    if (!res) return;
    const data = await res.json();
    if (!res.ok) { showToast(data.detail || 'Submission failed', 'error'); return; }

    renderTestResult(data);
  } catch (err) {
    hideLoading();
    showToast('Failed to submit test', 'error');
    console.error(err);
  }
}

function renderTestResult(result) {
  document.getElementById('mcq-start-screen').style.display = 'none';
  document.getElementById('mcq-quiz-screen').style.display = 'none';
  const screen = document.getElementById('mcq-result-screen');
  screen.style.display = 'block';

  const pct = result.percentage || 0;
  const circumference = 2 * Math.PI * 65;
  const offset = circumference - (pct / 100) * circumference;
  const scoreColor = pct >= 70 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)';

  screen.innerHTML = `
    <!-- Score Ring -->
    <div class="result-hero">
      <div class="result-score-ring">
        <svg width="160" height="160">
          <circle cx="80" cy="80" r="65" fill="none" stroke="var(--bg-tertiary)" stroke-width="10"/>
          <circle cx="80" cy="80" r="65" fill="none" stroke="${scoreColor}" stroke-width="10"
            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" stroke-linecap="round"
            style="transition:stroke-dashoffset 1s ease"/>
        </svg>
        <div class="score-text">
          <div class="score-value" style="color:${scoreColor}">${pct}%</div>
          <div class="score-label">Score</div>
        </div>
      </div>
      <div class="result-grade" style="color:${scoreColor}">Grade: ${result.grade || 'N/A'}</div>
    </div>

    <!-- Stats Grid -->
    <div class="result-stats-grid">
      <div class="result-stat-card"><div class="stat-icon green" style="width:36px;height:36px;border-radius:8px;font-size:1rem">✅</div><div class="stat-value" style="color:var(--success)">${result.correct || 0}</div><div class="stat-label">Correct</div></div>
      <div class="result-stat-card"><div class="stat-icon red" style="width:36px;height:36px;border-radius:8px;font-size:1rem">❌</div><div class="stat-value" style="color:var(--danger)">${result.wrong || 0}</div><div class="stat-label">Wrong</div></div>
      <div class="result-stat-card"><div class="stat-icon orange" style="width:36px;height:36px;border-radius:8px;font-size:1rem">⏭️</div><div class="stat-value">${result.skipped || 0}</div><div class="stat-label">Skipped</div></div>
      <div class="result-stat-card"><div class="stat-icon blue" style="width:36px;height:36px;border-radius:8px;font-size:1rem">⏱️</div><div class="stat-value">${result.time_taken || '0m 0s'}</div><div class="stat-label">Time Taken</div></div>
      <div class="result-stat-card"><div class="stat-icon purple" style="width:36px;height:36px;border-radius:8px;font-size:1rem">🎯</div><div class="stat-value">${result.accuracy || '0%'}</div><div class="stat-label">Accuracy</div></div>
      <div class="result-stat-card"><div class="stat-icon green" style="width:36px;height:36px;border-radius:8px;font-size:1rem">💪</div><div class="stat-value" style="font-size:0.85rem">${escapeHtml(result.strong_topics || 'None')}</div><div class="stat-label">Strong Topics</div></div>
      <div class="result-stat-card"><div class="stat-icon red" style="width:36px;height:36px;border-radius:8px;font-size:1rem">⚠️</div><div class="stat-value" style="font-size:0.85rem">${escapeHtml(result.weak_topics || 'None')}</div><div class="stat-label">Weak Topics</div></div>
    </div>

    <!-- Answer Review -->
    <div class="section-header mt-6"><h2>📋 Answer Review</h2></div>
    <div id="answer-review-list">
      ${(result.graded_details || []).map((q, i) => {
        const cardClass = q.is_skipped ? 'skipped-card' : (q.is_correct ? 'correct-card' : 'wrong-card');
        const statusIcon = q.is_skipped ? '⏭️' : (q.is_correct ? '✅' : '❌');
        return `
          <div class="review-card ${cardClass}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px">
              <span style="font-size:0.78rem;color:var(--text-tertiary);font-weight:600">Q${i+1}</span>
              <span>${statusIcon}</span>
            </div>
            <div class="review-question">${escapeHtml(q.question)}</div>
            <div class="review-answer-row">
              <span class="label">Your Answer:</span>
              <span>${q.is_skipped ? '<span style="color:var(--text-tertiary)">Skipped</span>' : escapeHtml(q.student_answer)} ${!q.is_skipped && !q.is_correct ? '❌' : ''}</span>
            </div>
            <div class="review-answer-row">
              <span class="label">Correct Answer:</span>
              <span style="color:var(--success)">${escapeHtml(q.correct_answer)} ✅</span>
            </div>
            <div class="review-explanation">
              <strong>Explanation:</strong> ${escapeHtml(q.explanation || 'No explanation available.')}
            </div>
            <div class="review-meta">
              ${priorityBadge(q.priority)}
              ${difficultyBadge(q.difficulty)}
              <span class="badge badge-info">${q.marks || 1} Mark${q.marks > 1 ? 's' : ''}</span>
            </div>
          </div>`;
      }).join('')}
    </div>

    <!-- Actions -->
    <div style="text-align:center;margin-top:28px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <button class="btn btn-primary btn-lg" onclick="resetMcq()">🔄 Take Another Test</button>
      <button class="btn btn-secondary btn-lg" onclick="switchSection('dashboard')">📊 Go to Dashboard</button>
    </div>
  `;
}

function resetMcq() {
  mcqQuestions = [];
  mcqAnswers = {};
  currentQIndex = 0;
  mcqTestId = null;
  totalSeconds = 20 * 60;
  if (timerInterval) clearInterval(timerInterval);

  document.getElementById('mcq-start-screen').style.display = 'block';
  document.getElementById('mcq-quiz-screen').style.display = 'none';
  document.getElementById('mcq-result-screen').style.display = 'none';
}
