/**
 * Encryption JavaScript
 */

let currentAlgorithm = 'caesar';

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadUsers();
    setupForms();
});

function selectAlgorithm(algorithm) {
    currentAlgorithm = algorithm;

    // Update button states
    document.querySelectorAll('.algorithm-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${algorithm}`).classList.add('active');

    // Update key labels
    const keyLabels = {
        'caesar': 'Shift (0-25)',
        'hill': 'Key (4 letters)',
        'playfair': 'Keyword'
    };

    const keyPlaceholders = {
        'caesar': '3',
        'hill': 'HILL',
        'playfair': 'SECRET'
    };

    document.getElementById('key-label-encrypt').textContent = keyLabels[algorithm];
    document.getElementById('key-label-decrypt').textContent = keyLabels[algorithm];
    document.getElementById('key-encrypt').placeholder = keyPlaceholders[algorithm];
    document.getElementById('key-decrypt').placeholder = keyPlaceholders[algorithm];
    document.getElementById('key-encrypt').value = keyPlaceholders[algorithm];
    document.getElementById('key-decrypt').value = keyPlaceholders[algorithm];
}

async function loadUsers() {
    try {
        const data = await apiRequest('/users');
        if (data && data.success) {
            const select = document.getElementById('receiver');
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

function setupForms() {
    document.getElementById('encrypt-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await encryptMessage();
    });

    document.getElementById('decrypt-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await decryptMessage();
    });
}

async function encryptMessage() {
    const plaintext = document.getElementById('plaintext').value;
    const key = document.getElementById('key-encrypt').value;
    const receiverId = document.getElementById('receiver').value;

    if (!plaintext.trim()) {
        alert('⚠️ Please enter a message to encrypt');
        return;
    }

    if (!key.trim()) {
        alert('⚠️ Please enter an encryption key');
        return;
    }

    try {
        const data = await apiRequest(`/encrypt/${currentAlgorithm}`, {
            method: 'POST',
            body: JSON.stringify({
                plaintext,
                shift: currentAlgorithm === 'caesar' ? parseInt(key) : undefined,
                key: currentAlgorithm !== 'caesar' ? key : undefined
            })
        });

        if (data && data.success) {
            document.getElementById('encrypted-text').textContent = data.encrypted;
            document.getElementById('encrypt-result').classList.remove('hidden');

            // Send message if receiver selected
            if (receiverId && receiverId !== '') {
                await sendMessage(receiverId, data.encrypted, key);
            } else {
                alert('✅ Message encrypted successfully!\n\n💡 Tip: Select a receiver to send this encrypted message to another user.');
            }
        } else {
            alert('❌ Encryption failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Encryption failed. Please check your input and try again.');
        console.error('Encryption error:', error);
    }
}

async function decryptMessage() {
    const ciphertext = document.getElementById('ciphertext').value;
    const key = document.getElementById('key-decrypt').value;

    if (!ciphertext.trim()) {
        alert('⚠️ Please enter an encrypted message to decrypt');
        return;
    }

    if (!key.trim()) {
        alert('⚠️ Please enter the decryption key');
        return;
    }

    try {
        const data = await apiRequest(`/decrypt/${currentAlgorithm}`, {
            method: 'POST',
            body: JSON.stringify({
                ciphertext,
                shift: currentAlgorithm === 'caesar' ? parseInt(key) : undefined,
                key: currentAlgorithm !== 'caesar' ? key : undefined
            })
        });

        if (data && data.success) {
            document.getElementById('decrypted-text').textContent = data.decrypted;
            document.getElementById('decrypt-result').classList.remove('hidden');
            alert('✅ Message decrypted successfully!');
        } else {
            alert('❌ Decryption failed: ' + (data.message || 'Wrong key or invalid ciphertext'));
        }
    } catch (error) {
        alert('❌ Decryption failed. Please check your key and try again.');
        console.error('Decryption error:', error);
    }
}

async function sendMessage(receiverId, encryptedText, key) {
    try {
        const data = await apiRequest('/messages/send', {
            method: 'POST',
            body: JSON.stringify({
                receiver_id: parseInt(receiverId),
                algorithm: currentAlgorithm,
                encrypted_text: encryptedText,
                key_used: key
            })
        });

        if (data && data.success) {
            alert('✅ Message encrypted and sent successfully!\n\n📨 The receiver can decrypt it in their inbox using the key: ' + key);
            // Clear the form
            document.getElementById('plaintext').value = '';
            document.getElementById('receiver').selectedIndex = 0;
        } else {
            alert('❌ Failed to send message: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Failed to send message. Please try again.');
        console.error('Send message error:', error);
    }
}

function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}
