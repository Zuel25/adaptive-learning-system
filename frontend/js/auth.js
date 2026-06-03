/**
 * Authentication Module
 * Menangani login, register, dan session management
 */

class AuthManager {
  constructor() {
    this.user = this.getUserFromStorage();
    this.token = api.getTokenFromStorage();
  }

  getUserFromStorage() {
    const userJSON = localStorage.getItem('user');
    return userJSON ? JSON.parse(userJSON) : null;
  }

  setUser(user) {
    this.user = user;
    localStorage.setItem('user', JSON.stringify(user));
  }

  removeUser() {
    this.user = null;
    localStorage.removeItem('user');
  }

  isLoggedIn() {
    return !!this.token && !!this.user;
  }

  async register(name, email, password, confirmPassword, role) {
    // Validasi
    if (!name || !email || !password || !confirmPassword || !role) {
      throw new Error('Semua field wajib diisi');
    }

    if (name.length < 3) {
      throw new Error('Nama minimal 3 karakter');
    }

    if (!this.validateEmail(email)) {
      throw new Error('Format email tidak valid');
    }

    if (password.length < 6) {
      throw new Error('Password minimal 6 karakter');
    }

    if (password !== confirmPassword) {
      throw new Error('Password tidak cocok');
    }

    if (!this.validatePassword(password)) {
      throw new Error('Password harus mengandung huruf besar, huruf kecil, dan angka');
    }

    try {
      const response = await api.register(name, email, password, role);
      
      api.setToken(response.token);
      this.setUser(response.user);
      
      return response;
    } catch (error) {
      throw new Error(error.message);
    }
  }

  async login(email, password) {
    // Validasi
    if (!email || !password) {
      throw new Error('Email dan password wajib diisi');
    }

    if (!this.validateEmail(email)) {
      throw new Error('Format email tidak valid');
    }

    try {
      const response = await api.login(email, password);
      
      api.setToken(response.token);
      this.setUser(response.user);
      
      return response;
    } catch (error) {
      throw new Error(error.message);
    }
  }

  async logout() {
    try {
      await api.logout();
      this.removeUser();
      api.setToken(null);
      window.location.href = '/index.html';
    } catch (error) {
      console.error('Logout error:', error);
      this.removeUser();
      api.setToken(null);
      window.location.href = '/index.html';
    }
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validatePassword(password) {
    // Harus mengandung huruf besar, huruf kecil, dan angka
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    return hasUpperCase && hasLowerCase && hasNumber;
  }
}

// Initialize auth manager
const auth = new AuthManager();
