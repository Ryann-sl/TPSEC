/**
 * Inbox JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadMessages();
});

async function loadMessages() {
    const container = document.getElementById('messages-container');

    try {
        const data = await apiRequest('/messages/inbox');

        if (data && data.success) {
            if (data.messages.length === 0) {
                container.innerHTML = '<div class="card text-center"><p>No messages yet</p></div>';
                return;
            }

            container.innerHTML = '';
            data.messages.forEach(message => {
                container.appendChild(createMessageCard(message));
            });
        }
    } catch (error) {
        container.innerHTML = '<div class="alert alert-error">Failed to load messages</div>';
    }
}

function createMessageCard(message) {
    const card = document.createElement('div');
    card.className = `card message-card ${!message.is_read ? 'unread' : ''}`;
    card.id = `message-${message.id}`;

    card.innerHTML = `
        <div class="message-header">
            <div>
                <strong>From: ${message.sender_username}</strong>
                ${!message.is_read ? '<span class="badge badge-success ml-2">New</span>' : ''}
            </div>
            <div class="message-meta">
                <span class="badge badge-info">${message.algorithm.toUpperCase()}</span>
                ${new Date(message.timestamp).toLocaleString()}
            </div>
        </div>
        
        <div class="encrypted-text">
            <strong>Encrypted:</strong> ${message.encrypted_text}
        </div>
        
        <div class="decrypt-form">
            <div class="form-group">
                <label class="form-label">Enter Key to Decrypt</label>
                <input type="text" id="key-${message.id}" class="form-input" placeholder="Enter decryption key">
            </div>
            <button class="btn btn-primary" onclick="decryptMessage(${message.id}, '${message.algorithm}', '${message.encrypted_text}')">
                🔓 Decrypt
            </button>
        </div>
        
        <div id="decrypted-${message.id}" class="hidden mt-3">
            <h4>Decrypted Message:</h4>
            <div class="result-box" id="result-${message.id}"></div>
        </div>
    `;

    return card;
}

async function decryptMessage(messageId, algorithm, encryptedText) {
    const key = document.getElementById(`key-${messageId}`).value;

    if (!key) {
        alert('Please enter a key');
        return;
    }

    try {
        const data = await apiRequest(`/decrypt/${algorithm}`, {
            method: 'POST',
            body: JSON.stringify({
                ciphertext: encryptedText,
                shift: algorithm === 'caesar' ? parseInt(key) : undefined,
                key: algorithm !== 'caesar' ? key : undefined
            })
        });

        if (data && data.success) {
            document.getElementById(`result-${messageId}`).textContent = data.decrypted;
            document.getElementById(`decrypted-${messageId}`).classList.remove('hidden');

            // Mark as read
            await apiRequest(`/messages/${messageId}/read`, { method: 'PUT' });

            // Update UI
            const card = document.getElementById(`message-${messageId}`);
            card.classList.remove('unread');
            const badge = card.querySelector('.badge-success');
            if (badge) badge.remove();
        }
    } catch (error) {
        alert('Decryption failed. Check your key.');
    }
}
