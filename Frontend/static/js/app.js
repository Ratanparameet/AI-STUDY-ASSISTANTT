// ===========================================================
// App Shell — Sidebar Navigation, Theme, Toasts, Loading
// ===========================================================

// ---- Toast Notifications ----
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  toast.innerHTML = `<span>${icons[type] || ''} ${message}</span><button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentElement) toast.remove(); }, 4000);
}

// ---- Loading Overlay ----
function showLoading(text = 'Loading...') {
  const el = document.getElementById('loading-overlay');
  const txt = document.getElementById('loading-text');
  if (el) { el.classList.remove('hidden'); }
  if (txt) { txt.textContent = text; }
}

function hideLoading() {
  const el = document.getElementById('loading-overlay');
  if (el) { el.classList.add('hidden'); }
}

// ---- Theme Toggle ----
function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) btn.textContent = saved === 'dark' ? '🌙' : '☀️';
  const settingToggle = document.getElementById('setting-dark-mode');
  if (settingToggle) settingToggle.checked = saved === 'dark';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) btn.textContent = next === 'dark' ? '🌙' : '☀️';
  const settingToggle = document.getElementById('setting-dark-mode');
  if (settingToggle) settingToggle.checked = next === 'dark';
}

// ---- Sidebar Navigation ----
function initSidebar() {
  const navItems = document.querySelectorAll('.nav-item[data-section]');
  const sections = document.querySelectorAll('.content-section');
  const pageTitle = document.getElementById('page-title');
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  const titles = {
    'dashboard': 'Dashboard',
    'pdf-analyzer': '📄 Question Paper Analyzer',
    'mcq-test': '🧠 MCQ Practice',
    'study-planner': '📅 Study Planner',
    'pyq-checker': '🔍 PYQ Priority Check',
    'history': '📜 History',
    'profile': '👤 Profile',
    'settings': '⚙️ Settings'
  };

  function switchSection(sectionId) {
    sections.forEach(s => s.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));
    
    const target = document.getElementById('section-' + sectionId);
    if (target) target.classList.add('active');
    
    const nav = document.querySelector(`.nav-item[data-section="${sectionId}"]`);
    if (nav) nav.classList.add('active');
    
    if (pageTitle) pageTitle.textContent = titles[sectionId] || sectionId;

    // Close mobile sidebar
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');

    // Trigger section-specific load
    if (sectionId === 'dashboard' && typeof loadDashboard === 'function') loadDashboard();
    if (sectionId === 'history' && typeof loadHistory === 'function') loadHistory();
    if (sectionId === 'profile' && typeof loadProfile === 'function') loadProfile();
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      switchSection(item.dataset.section);
    });
  });

  // Mobile menu toggle
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('visible');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('visible');
    });
  }

  // Make switchSection globally accessible
  window.switchSection = switchSection;
}

// ---- Sidebar User Info ----
function updateSidebarUser() {
  const name = Auth.getUsername();
  const email = Auth.getEmail();
  const initial = name ? name.charAt(0).toUpperCase() : 'S';

  const nameEl = document.getElementById('user-name-sidebar');
  const emailEl = document.getElementById('user-email-sidebar');
  const avatarEl = document.getElementById('user-avatar-sidebar');

  if (nameEl) nameEl.textContent = name;
  if (emailEl) emailEl.textContent = email;
  if (avatarEl) avatarEl.textContent = initial;
}

// ---- Logout ----
function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (btn) {
    btn.addEventListener('click', () => {
      Auth.logout();
    });
  }
}

// ---- Escape HTML ----
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---- Priority Badge ----
function priorityBadge(priority) {
  const p = (priority || '').toLowerCase();
  if (p === 'high') return '<span class="badge badge-high">High</span>';
  if (p === 'medium') return '<span class="badge badge-medium">Medium</span>';
  return '<span class="badge badge-low">Low</span>';
}

function difficultyBadge(difficulty) {
  const d = (difficulty || '').toLowerCase();
  if (d === 'hard') return '<span class="badge badge-hard">Hard</span>';
  if (d === 'easy') return '<span class="badge badge-easy">Easy</span>';
  return '<span class="badge badge-warning">Medium</span>';
}

// ---- Init Everything ----
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  updateSidebarUser();
  initLogout();

  // Theme toggle button
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // Settings dark mode toggle
  const settingDark = document.getElementById('setting-dark-mode');
  if (settingDark) {
    settingDark.addEventListener('change', () => {
      const theme = settingDark.checked ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      const btn = document.getElementById('theme-toggle-btn');
      if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
    });
  }

  // Load dashboard on start
  if (typeof loadDashboard === 'function') loadDashboard();
});
