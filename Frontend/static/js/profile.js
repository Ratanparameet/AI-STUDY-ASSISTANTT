// ===========================================================
// Profile & Settings
// ===========================================================

async function loadProfile() {
  try {
    const res = await Auth.fetchWithAuth('/profile');
    if (!res) return;
    const data = await res.json();
    if (!res.ok) return;

    const name = data.name || 'Student';
    const email = data.email || '';
    const initial = name.charAt(0).toUpperCase();

    // Profile header
    setText('profile-name', name);
    setText('profile-email', email);
    const avatarEl = document.getElementById('profile-avatar-large');
    if (avatarEl) avatarEl.textContent = initial;
    setText('profile-branch', data.branch || '—');
    setText('profile-semester', data.semester ? `Sem ${data.semester}` : '—');

    // Edit form
    setVal('edit-name', name);
    setVal('edit-email', email);
    setVal('edit-college', data.college || '');
    setVal('edit-branch', data.branch || '');
    setVal('edit-semester', data.semester || '');
  } catch (err) {
    console.error('Profile load error:', err);
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function setVal(id, value) {
  const el = document.getElementById(id);
  if (el) el.value = value;
}

// Profile form submit
document.addEventListener('DOMContentLoaded', () => {
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      try {
        const res = await Auth.fetchWithAuth('/update-profile', {
          method: 'POST',
          headers: Auth.getHeaders(),
          body: JSON.stringify({
            name: document.getElementById('edit-name').value.trim(),
            email: document.getElementById('edit-email').value.trim(),
            college: document.getElementById('edit-college').value.trim(),
            branch: document.getElementById('edit-branch').value.trim(),
            semester: document.getElementById('edit-semester').value.trim(),
            profile_photo: ''
          })
        });

        if (!res) return;
        const data = await res.json();

        if (res.ok && data.success) {
          // Update localStorage
          localStorage.setItem('username', document.getElementById('edit-name').value.trim());
          localStorage.setItem('user_email', document.getElementById('edit-email').value.trim());
          updateSidebarUser();
          loadProfile();
          showToast('Profile updated successfully!', 'success');
        } else {
          showToast(data.detail || 'Update failed', 'error');
        }
      } catch (err) {
        showToast('Failed to update profile', 'error');
      }
    });
  }

  // Change password form
  const pwdForm = document.getElementById('change-pwd-form');
  if (pwdForm) {
    pwdForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const oldPwd = document.getElementById('current-pwd').value;
      const newPwd = document.getElementById('new-pwd').value;

      if (!oldPwd || !newPwd) {
        showToast('Please fill in both fields', 'warning');
        return;
      }

      try {
        const res = await Auth.fetchWithAuth('/change-password', {
          method: 'POST',
          headers: Auth.getHeaders(),
          body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
        });

        if (!res) return;
        const data = await res.json();

        if (res.ok && data.success) {
          showToast('Password changed successfully!', 'success');
          document.getElementById('current-pwd').value = '';
          document.getElementById('new-pwd').value = '';
        } else {
          showToast(data.detail || 'Password change failed', 'error');
        }
      } catch (err) {
        showToast('Failed to change password', 'error');
      }
    });
  }

  // Save settings
  const saveSettingsBtn = document.getElementById('save-settings-btn');
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', async () => {
      const theme = document.getElementById('setting-dark-mode').checked ? 'dark' : 'light';
      const notifications = document.getElementById('setting-notifications').checked;
      const autoSave = document.getElementById('setting-auto-save').checked;
      const language = document.getElementById('setting-language').value;

      try {
        const res = await Auth.fetchWithAuth('/settings', {
          method: 'POST',
          headers: Auth.getHeaders(),
          body: JSON.stringify({
            theme: theme,
            notifications_enabled: notifications,
            auto_save: autoSave,
            language: language,
            theme_color: '#a855f7'
          })
        });

        if (!res) return;
        const data = await res.json();

        if (res.ok && data.success) {
          showToast('Settings saved!', 'success');
        } else {
          showToast(data.detail || 'Failed to save settings', 'error');
        }
      } catch (err) {
        showToast('Failed to save settings', 'error');
      }
    });
  }

  // Load settings on init
  loadSettings();
});

async function loadSettings() {
  try {
    const res = await Auth.fetchWithAuth('/settings');
    if (!res) return;
    const data = await res.json();
    if (!res.ok) return;

    const darkToggle = document.getElementById('setting-dark-mode');
    const notifToggle = document.getElementById('setting-notifications');
    const autoSaveToggle = document.getElementById('setting-auto-save');

    if (darkToggle) darkToggle.checked = data.theme === 'dark';
    if (notifToggle) notifToggle.checked = data.notifications_enabled;
    if (autoSaveToggle) autoSaveToggle.checked = data.auto_save;

    // Apply saved theme
    if (data.theme) {
      document.documentElement.setAttribute('data-theme', data.theme);
      localStorage.setItem('theme', data.theme);
      const btn = document.getElementById('theme-toggle-btn');
      if (btn) btn.textContent = data.theme === 'dark' ? '🌙' : '☀️';
    }
  } catch (err) {
    console.error('Settings load error:', err);
  }
}

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
