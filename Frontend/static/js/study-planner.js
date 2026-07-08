// ===========================================================
// Study Planner — Generate & Render Study Plan
// ===========================================================

async function generateStudyPlan(report) {
  showLoading('Generating personalized study plan...');

  try {
    const res = await Auth.fetchWithAuth('/study-plan', {
      method: 'POST',
      headers: Auth.getHeaders(),
      body: JSON.stringify({ report: report || {} })
    });

    hideLoading();
    if (!res) return;
    const data = await res.json();
    if (!res.ok) { showToast(data.detail || 'Failed to generate plan', 'error'); return; }

    renderStudyPlan(data);
    showToast('Study plan generated!', 'success');

    // Switch to study planner section
    if (typeof switchSection === 'function') switchSection('study-planner');
  } catch (err) {
    hideLoading();
    showToast('Failed to generate study plan', 'error');
    console.error(err);
  }
}

function renderStudyPlan(data) {
  const container = document.getElementById('study-plan-content');
  if (!container) return;

  const plan = data.plan || [];
  const subject = data.subject || 'General';

  if (plan.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📅</div>
        <h3>No Topics Available</h3>
        <p>Upload a question paper and analyze it first to generate a study plan.</p>
      </div>`;
    return;
  }

  // Summary cards
  let html = `
    <div class="report-grid mb-6">
      <div class="report-card"><div class="report-value">${escapeHtml(subject)}</div><div class="report-label">Subject</div></div>
      <div class="report-card"><div class="report-value">${data.estimated_completion || '3 Days'}</div><div class="report-label">Estimated Completion</div></div>
      <div class="report-card"><div class="report-value">${data.hours_needed || 12}h</div><div class="report-label">Study Hours</div></div>
      <div class="report-card">
        <div class="report-value">${data.progress || 0}%</div>
        <div class="report-label">Progress</div>
        <div class="progress-bar mt-2"><div class="progress-fill" style="width:${data.progress || 0}%"></div></div>
      </div>
    </div>
  `;

  // Timeline
  html += '<div class="plan-timeline">';
  plan.forEach(day => {
    html += `
      <div class="plan-day-card">
        <div class="plan-day-title">${escapeHtml(day.day)}</div>
        <ul class="plan-topic-list">
          ${(day.topics || []).map(topic => `<li class="plan-topic-item">${escapeHtml(topic)}</li>`).join('')}
        </ul>
        <div class="plan-meta">
          <span>⏱️ ${day.hours || 4} hours</span>
          <span>📊 Target: ${day.completion || 100}%</span>
        </div>
      </div>`;
  });
  html += '</div>';

  container.innerHTML = html;
}
