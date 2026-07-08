// ===========================================================
// PDF Analyzer — Upload, Analysis Table, Filters, Report
// ===========================================================
let analysisData = null; // Stores the full analysis response
let filteredQuestions = [];

document.addEventListener('DOMContentLoaded', () => {
  initPdfUpload();
  initAnalysisFilters();
});

function initPdfUpload() {
  const zone = document.getElementById('pdf-upload-zone');
  const fileInput = document.getElementById('pdf-file-input');
  if (!zone || !fileInput) return;

  // Drag & drop
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.toLowerCase().endsWith('.pdf')) {
      uploadPdf(files[0]);
    } else {
      showToast('Please upload a PDF file', 'warning');
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      uploadPdf(fileInput.files[0]);
    }
  });
}

async function uploadPdf(file) {
  showLoading('Analyzing question paper...');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/upload-pdf', {
      method: 'POST',
      headers: Auth.getUploadHeaders(),
      body: formData
    });

    if (!res) { hideLoading(); showToast('Authentication error', 'error'); return; }
    if (res.status === 401) { Auth.logout(); return; }

    const data = await res.json();
    hideLoading();

    if (!res.ok) {
      showToast(data.detail || 'Upload failed', 'error');
      return;
    }

    analysisData = data;
    filteredQuestions = data.questions || [];
    showToast(`Analyzed ${filteredQuestions.length} questions from ${escapeHtml(file.name)}`, 'success');
    renderAnalysisResults();
  } catch (err) {
    hideLoading();
    showToast('Upload failed. Is the backend running?', 'error');
    console.error('PDF upload error:', err);
  }
}

function renderAnalysisResults() {
  if (!analysisData) return;

  const resultsDiv = document.getElementById('pdf-analysis-results');
  if (resultsDiv) resultsDiv.style.display = 'block';

  // Hide upload zone
  const uploadZone = document.getElementById('pdf-upload-zone');
  if (uploadZone) uploadZone.style.display = 'none';

  // Render report cards
  renderReportCards(analysisData.report);

  // Render table
  renderAnalysisTable(filteredQuestions);
}

function renderReportCards(report) {
  const grid = document.getElementById('report-grid');
  if (!grid || !report) return;

  grid.innerHTML = `
    <div class="report-card"><div class="report-value">${report.total_questions || 0}</div><div class="report-label">Total Questions</div></div>
    <div class="report-card"><div class="report-value" style="color:var(--danger)">${report.high_priority || 0}</div><div class="report-label">High Priority</div></div>
    <div class="report-card"><div class="report-value" style="color:var(--warning)">${report.medium_priority || 0}</div><div class="report-label">Medium Priority</div></div>
    <div class="report-card"><div class="report-value" style="color:var(--success)">${report.low_priority || 0}</div><div class="report-label">Low Priority</div></div>
    <div class="report-card"><div class="report-value">${escapeHtml(report.most_repeated_chapter || 'N/A')}</div><div class="report-label">Most Repeated Chapter</div></div>
    <div class="report-card"><div class="report-value">${escapeHtml(report.weak_chapters || 'N/A')}</div><div class="report-label">Weak Chapters</div></div>
    <div class="report-card"><div class="report-value">${escapeHtml(report.recommended_study_time || 'N/A')}</div><div class="report-label">Recommended Study Time</div></div>
    <div class="report-card"><div class="report-value" style="color:var(--accent)">${escapeHtml(report.estimated_coverage || '0%')}</div><div class="report-label">Estimated Coverage</div></div>
  `;
}

function renderAnalysisTable(questions) {
  const tbody = document.getElementById('analysis-tbody');
  if (!tbody) return;

  if (!questions || questions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:32px;color:var(--text-tertiary)">No questions found</td></tr>';
    return;
  }

  tbody.innerHTML = questions.map((q, i) => {
    const priority = q.priority || 'Low';
    const difficulty = q.difficulty || 'Medium';
    const recClass = q.recommendation === 'Study First' ? 'badge-high' : 'badge-info';
    
    return `
      <tr>
        <td>${i + 1}</td>
        <td class="question-cell" title="${escapeHtml(q.question)}">${escapeHtml(q.question)}</td>
        <td>${priorityBadge(priority)}</td>
        <td><strong>${q.importance || 0}%</strong></td>
        <td>${q.repeated || 0} times</td>
        <td>${difficultyBadge(difficulty)}</td>
        <td>${q.avg_marks || 0}</td>
        <td><span class="badge ${recClass}">${escapeHtml(q.recommendation || 'Review')}</span></td>
      </tr>`;
  }).join('');
}

function initAnalysisFilters() {
  // Filter chips
  const filterBar = document.getElementById('analysis-filter-bar');
  if (filterBar) {
    filterBar.addEventListener('click', e => {
      const chip = e.target.closest('.filter-chip');
      if (!chip) return;

      filterBar.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const filter = chip.dataset.filter;
      if (!analysisData) return;

      if (filter === 'all') {
        filteredQuestions = analysisData.questions || [];
      } else {
        filteredQuestions = (analysisData.questions || []).filter(q => q.priority === filter);
      }

      renderAnalysisTable(filteredQuestions);
    });
  }

  // Sort select
  const sortSelect = document.getElementById('analysis-sort');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      const sortBy = sortSelect.value;
      const sorted = [...filteredQuestions];

      sorted.sort((a, b) => {
        if (sortBy === 'importance') return (b.importance || 0) - (a.importance || 0);
        if (sortBy === 'repeated') return (b.repeated || 0) - (a.repeated || 0);
        if (sortBy === 'marks') return (b.avg_marks || 0) - (a.avg_marks || 0);
        if (sortBy === 'difficulty') {
          const order = { 'Hard': 3, 'Medium': 2, 'Easy': 1 };
          return (order[b.difficulty] || 0) - (order[a.difficulty] || 0);
        }
        return 0;
      });

      filteredQuestions = sorted;
      renderAnalysisTable(sorted);
    });
  }

  // Generate MCQ from PDF
  const mcqBtn = document.getElementById('generate-mcq-from-pdf');
  if (mcqBtn) {
    mcqBtn.addEventListener('click', () => {
      if (analysisData && analysisData.report) {
        const subject = analysisData.report.subject || 'Embedded Systems';
        const selectEl = document.getElementById('mcq-subject-select');
        if (selectEl) selectEl.value = subject;
      }
      if (typeof switchSection === 'function') switchSection('mcq-test');
    });
  }

  // Generate Study Plan
  const planBtn = document.getElementById('generate-study-plan-btn');
  if (planBtn) {
    planBtn.addEventListener('click', () => {
      if (typeof generateStudyPlan === 'function' && analysisData) {
        generateStudyPlan(analysisData.report);
      }
      if (typeof switchSection === 'function') switchSection('study-planner');
    });
  }
}

// PYQ Priority Checker (single question)
document.addEventListener('DOMContentLoaded', () => {
  const checkBtn = document.getElementById('pyq-check-btn');
  if (checkBtn) {
    checkBtn.addEventListener('click', async () => {
      const input = document.getElementById('pyq-question-input');
      const resultArea = document.getElementById('pyq-result-area');
      if (!input || !resultArea) return;

      const question = input.value.trim();
      if (!question) { showToast('Enter a question first', 'warning'); return; }

      checkBtn.disabled = true;
      checkBtn.textContent = 'Checking...';

      try {
        const res = await Auth.fetchWithAuth('/api/analyze-question', {
          method: 'POST',
          headers: Auth.getHeaders(),
          body: JSON.stringify({ question })
        });

        if (!res) { checkBtn.disabled = false; checkBtn.textContent = 'Check Priority'; return; }
        const data = await res.json();

        if (res.ok) {
          const p = data.priority || 'Low';
          resultArea.innerHTML = `
            <div class="glass-card" style="margin-top:16px">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:16px">
                <div>
                  <strong style="font-size:1.1rem">${escapeHtml(data.matched_topic || data.question)}</strong>
                  <div style="font-size:0.82rem;color:var(--text-tertiary);margin-top:4px">${escapeHtml(data.subject || 'Unknown')} • ${escapeHtml(data.section || '')}</div>
                </div>
                ${priorityBadge(p)}
              </div>
              <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:0.88rem;color:var(--text-secondary)">
                <span>📊 Repeated: <strong>${data.times_repeated || 'N/A'}</strong></span>
                <span>📈 Repeat %: <strong>${data.repeat_percentage != null ? data.repeat_percentage + '%' : 'N/A'}</strong></span>
                <span>📝 Source: <strong>${data.source === 'pyq_history' ? 'Past Papers' : 'AI Estimate'}</strong></span>
              </div>
              ${data.marks && data.marks.length ? `<div style="margin-top:12px;font-size:0.88rem">💯 Marks: ${data.marks.join(', ')}</div>` : ''}
              ${data.note ? `<div style="margin-top:12px;padding:12px;background:var(--bg-glass);border-radius:var(--radius);font-size:0.85rem;color:var(--text-tertiary)">${escapeHtml(data.note)}</div>` : ''}
            </div>`;
        } else {
          showToast(data.detail || 'Error checking priority', 'error');
        }
      } catch (err) {
        showToast('Could not reach backend', 'error');
      } finally {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Check Priority';
      }
    });
  }
});
