/**
 * Authentication JavaScript
 * Handles login, registration, and token management
 */

const API_URL = 'http://localhost:5000/api';

// Show alert message
function showAlert(message, type = 'info') {
    const container = document.getElementById('alert-container');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    container.innerHTML = '';
    container.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Store token
function setToken(token) {
    localStorage.setItem('token', token);
}

// Get token
function getToken() {
    return localStorage.getItem('token');
}

// Store user info
function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

// Get user info
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Clear auth data
function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Check if authenticated
function isAuthenticated() {
    return !!getToken();
}

// Require authentication
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Register user
async function register(username, password) {
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            showAlert('Registration successful! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('Registration failed. Please try again.', 'error');
        console.error('Registration error:', error);
    }
}

// Login user
async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            setToken(data.token);
            setUser({
                id: data.user_id,
                username: data.username
            });

            showAlert('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('Login failed. Please try again.', 'error');
        console.error('Login error:', error);
    }
}

// Logout user
function logout() {
    clearAuth();
    window.location.href = 'index.html';
}

// Navigate to page
function navigateTo(page) {
    window.location.href = page;
}

// API request with auth
async function apiRequest(endpoint, options = {}) {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json();

        // Handle unauthorized
        if (response.status === 401) {
            clearAuth();
            window.location.href = 'index.html';
            return null;
        }

        return data;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}
