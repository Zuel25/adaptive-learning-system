// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Login function
async function login(event) {
    if (event) event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    if (!email || !password || !role) {
        alert('Semua field harus diisi');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                role: role
            })
        });

        if (!response.ok) {
            throw new Error('Login gagal');
        }

        const data = await response.json();

        // Store token and user info
        localStorage.setItem('token', data.token);
        localStorage.setItem('role', role);

        if (role === 'student') {
            localStorage.setItem('studentId', data.user_id);
            localStorage.setItem('studentName', data.name);
            window.location.href = 'student/pretest.html';
        } else if (role === 'teacher') {
            localStorage.setItem('teacherId', data.user_id);
            localStorage.setItem('teacherName', data.name);
            window.location.href = 'teacher/dashboard.html';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Email atau password salah!');
    }
}

// Demo login function
function demoLogin(role) {
    if (role === 'student') {
        document.getElementById('email').value = 'student@example.com';
        document.getElementById('password').value = 'student123';
    } else if (role === 'teacher') {
        document.getElementById('email').value = 'teacher@example.com';
        document.getElementById('password').value = 'teacher123';
    }
    document.getElementById('role').value = role;
}

// Logout function
function logout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
        localStorage.clear();
        window.location.href = '../index.html';
    }
}

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (!token || !role) {
        window.location.href = '/index.html';
    }
}

// Get Authorization Header
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}