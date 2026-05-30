// Main App Logic

// Initialize login form
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', login);
}

// Utility function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('id-ID', options);
}

// Utility function to get level text
function getLevelText(level) {
    const levels = {
        'dasar': '🟢 Dasar',
        'menengah': '🟡 Menengah',
        'mahir': '🔴 Mahir'
    };
    return levels[level] || level;
}

// Utility function to get status badge
function getStatusBadge(status) {
    const badges = {
        'belum_pretest': '<span class="badge badge-warning">⏳ Belum Pre-test</span>',
        'learning': '<span class="badge badge-info">📚 Belajar</span>',
        'completed': '<span class="badge badge-success">✅ Selesai</span>',
        'in_progress': '<span class="badge badge-info">🔄 Sedang Berlangsung</span>'
    };
    return badges[status] || status;
}

// Debounce function for search
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 6px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Calculate learning progress
function calculateProgress(completedMaterials, totalMaterials) {
    if (totalMaterials === 0) return 0;
    return Math.round((completedMaterials / totalMaterials) * 100);
}

// Validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Get URL parameter
function getUrlParameter(name) {
    const url = new URL(window.location);
    return url.searchParams.get(name);
}

// Store user session
function setUserSession(userId, name, role, token) {
    localStorage.setItem('userId', userId);
    localStorage.setItem('userName', name);
    localStorage.setItem('userRole', role);
    localStorage.setItem('token', token);
}

// Get user session
function getUserSession() {
    return {
        userId: localStorage.getItem('userId'),
        userName: localStorage.getItem('userName'),
        userRole: localStorage.getItem('userRole'),
        token: localStorage.getItem('token')
    };
}

// Clear user session
function clearUserSession() {
    localStorage.clear();
}

// Fetch with authorization
async function authorizedFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(url, {
        ...options,
        headers
    });
}

// Handle API errors
function handleApiError(error) {
    console.error('API Error:', error);
    if (error.status === 401) {
        clearUserSession();
        window.location.href = '/index.html';
    }
    return {
        error: true,
        message: error.message || 'Terjadi kesalahan'
    };
}

// Export functions for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        getLevelText,
        getStatusBadge,
        debounce,
        showNotification,
        calculateProgress,
        isValidEmail,
        getUrlParameter,
        setUserSession,
        getUserSession,
        clearUserSession,
        authorizedFetch,
        handleApiError
    };
}