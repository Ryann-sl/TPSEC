/**
 * Dashboard JavaScript
 * Handles dashboard functionality
 */

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Require authentication
    if (!requireAuth()) return;

    // Display username
    const user = getUser();
    if (user) {
        const usernameDisplay = document.getElementById('username-display');
        if (usernameDisplay) {
            usernameDisplay.textContent = user.username;
        }
    }

    // Load inbox count
    loadInboxCount();
});

// Load inbox message count
async function loadInboxCount() {
    try {
        const data = await apiRequest('/messages/inbox');

        if (data && data.success) {
            const unreadCount = data.messages.filter(m => !m.is_read).length;

            const badge = document.getElementById('inbox-badge');
            if (badge && unreadCount > 0) {
                badge.textContent = `${unreadCount} New`;
                badge.className = 'badge badge-error module-badge';
            }
        }
    } catch (error) {
        console.error('Failed to load inbox count:', error);
    }
}
