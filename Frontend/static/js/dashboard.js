// ===========================================================
// Dashboard — Stats & Charts
// ===========================================================
let priorityChartInstance = null;
let scoresChartInstance = null;

async function loadDashboard() {
  try {
    const res = await Auth.fetchWithAuth('/history');
    if (!res) return;
    const data = await res.json();
    if (!res.ok) return;

    const stats = data.dashboard_stats || {};
    const userStats = data.user_stats || {};

    // Update stat cards
    setText('stat-pdfs', stats.uploaded_pdfs || 0);
    setText('stat-questions', stats.questions_analyzed || 0);
    setText('stat-mcqs', stats.mcqs_attempted || 0);
    setText('stat-avg-score', stats.avg_score || '0 / 20');
    setText('stat-hp', userStats.high_priority_left || stats.high_priority_completed || 0);
    setText('stat-weak', stats.weak_chapters || 'None');
    setText('stat-progress', stats.study_progress || '0%');

    const progressNum = parseInt(stats.study_progress) || 0;
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) progressFill.style.width = progressNum + '%';

    // Charts
    renderPriorityChart(data);
    renderScoresChart(data);
  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function renderPriorityChart(data) {
  const canvas = document.getElementById('chart-priority');
  if (!canvas) return;

  // Aggregate priority data from analysis history
  let high = 0, medium = 0, low = 0;
  if (data.analysis_history) {
    data.analysis_history.forEach(a => {
      const r = a.report || {};
      high += r.high_priority || 0;
      medium += r.medium_priority || 0;
      low += r.low_priority || 0;
    });
  }

  // Fallback if no data
  if (high === 0 && medium === 0 && low === 0) {
    high = 1; medium = 1; low = 1;
  }

  if (priorityChartInstance) priorityChartInstance.destroy();

  priorityChartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [high, medium, low],
        backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim(),
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 12,
            font: { family: 'Inter', size: 12 }
          }
        }
      }
    }
  });
}

function renderScoresChart(data) {
  const canvas = document.getElementById('chart-scores');
  if (!canvas) return;

  const testHistory = data.test_history || [];
  const labels = testHistory.map((_, i) => 'Test ' + (i + 1)).slice(-10);
  const scores = testHistory.map(t => t.percentage || 0).slice(-10);

  if (scores.length === 0) {
    labels.push('No tests yet');
    scores.push(0);
  }

  if (scoresChartInstance) scoresChartInstance.destroy();

  scoresChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Score %',
        data: scores,
        backgroundColor: 'rgba(124, 58, 237, 0.6)',
        borderColor: '#7c3aed',
        borderWidth: 1,
        borderRadius: 6,
        maxBarThickness: 40
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-tertiary').trim(),
            font: { family: 'Inter', size: 11 }
          },
          grid: { color: 'rgba(255,255,255,0.04)' }
        },
        x: {
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-tertiary').trim(),
            font: { family: 'Inter', size: 11 }
          },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// ---- History Section ----
async function loadHistory() {
  const container = document.getElementById('history-content');
  if (!container) return;

  try {
    const res = await Auth.fetchWithAuth('/history');
    if (!res) return;
    const data = await res.json();
    if (!res.ok) return;

    let html = '';

    // PDF Analysis History
    if (data.analysis_history && data.analysis_history.length > 0) {
      html += '<h3 style="font-family:var(--font-display);font-weight:700;margin-bottom:16px">📄 PDF Analysis History</h3>';
      html += '<div style="display:grid;gap:12px;margin-bottom:32px">';
      data.analysis_history.forEach(a => {
        const r = a.report || {};
        html += `
          <div class="glass-card" style="padding:18px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
              <div>
                <strong style="color:var(--text-primary)">${escapeHtml(a.filename || 'Unknown')}</strong>
                <div style="font-size:0.82rem;color:var(--text-tertiary);margin-top:4px">${a.questions_count || 0} questions • ${r.subject || 'General'}</div>
              </div>
              <div style="display:flex;gap:6px">
                <span class="badge badge-high">${r.high_priority || 0} High</span>
                <span class="badge badge-warning">${r.medium_priority || 0} Med</span>
                <span class="badge badge-success">${r.low_priority || 0} Low</span>
              </div>
            </div>
          </div>`;
      });
      html += '</div>';
    }

    // Test History
    if (data.test_history && data.test_history.length > 0) {
      html += '<h3 style="font-family:var(--font-display);font-weight:700;margin-bottom:16px">🧠 MCQ Test History</h3>';
      html += '<div style="display:grid;gap:12px">';
      data.test_history.forEach(t => {
        const color = t.percentage >= 70 ? 'var(--success)' : t.percentage >= 50 ? 'var(--warning)' : 'var(--danger)';
        html += `
          <div class="glass-card" style="padding:18px">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
              <div>
                <strong style="color:var(--text-primary)">${escapeHtml(t.subject || 'Test')}</strong>
                <div style="font-size:0.82rem;color:var(--text-tertiary);margin-top:4px">Score: ${t.score}/${t.total} • Grade: ${t.grade}</div>
              </div>
              <div style="font-family:var(--font-display);font-weight:800;font-size:1.3rem;color:${color}">${t.percentage}%</div>
            </div>
          </div>`;
      });
      html += '</div>';
    }

    if (!html) {
      html = '<div class="empty-state"><div class="empty-icon">📜</div><h3>No History Yet</h3><p>Your analysis and test history will appear here.</p></div>';
    }

    container.innerHTML = html;
  } catch (err) {
    console.error('History load error:', err);
  }
}
