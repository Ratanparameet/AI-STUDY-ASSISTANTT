// ===========================================================
// Auth Utility — JWT Token Management
// ===========================================================
const Auth = {
  getToken() {
    return localStorage.getItem('auth_token');
  },

  getHeaders() {
    const token = this.getToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  },

  getUploadHeaders() {
    const token = this.getToken();
    return { 'Authorization': `Bearer ${token}` };
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  getUsername() {
    return localStorage.getItem('username') || 'Student';
  },

  getEmail() {
    return localStorage.getItem('user_email') || '';
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_email');
    window.location.href = '/welcome';
  },

  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = '/welcome';
      return false;
    }
    return true;
  },

  async fetchWithAuth(url, options = {}) {
    if (!options.headers) {
      options.headers = this.getHeaders();
    }
    try {
      const res = await fetch(url, options);
      if (res.status === 401) {
        this.logout();
        return null;
      }
      return res;
    } catch (err) {
      console.error('Network error:', err);
      return null;
    }
  }
};

// Check auth on page load
if (!Auth.requireAuth()) {
  // Redirect happens inside requireAuth
}
