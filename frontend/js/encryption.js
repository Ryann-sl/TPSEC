/**
 * Encryption JavaScript
 */

let currentAlgorithm = 'playfair';
let isLocked = false;

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadUsers();
    setupForms();
    selectAlgorithm('playfair');
});

function selectAlgorithm(algorithm) {
    if (isLocked) {
        alert('⚠️ You are currently working with ' + currentAlgorithm.toUpperCase() + '. Please reset to change algorithms.');
        return;
    }
    currentAlgorithm = algorithm;

    // Update button states
    document.querySelectorAll('.algorithm-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`btn-${algorithm}`).classList.add('active');

    // Update key labels
    const keyLabels = {
        'caesar': 'Shift (0-25)',
        'hill': 'Key Matrix',
        'playfair': 'Keyword'
    };

    const keyPlaceholders = {
        'caesar': '3',
        'hill': '3 3 2 5',
        'playfair': 'SECRET'
    };

    document.getElementById('key-label-encrypt').textContent = keyLabels[algorithm];
    document.getElementById('key-label-decrypt').textContent = keyLabels[algorithm];

    // Toggle Matrix UI for Hill
    if (algorithm === 'hill') {
        document.getElementById('key-encrypt').classList.add('hidden');
        document.getElementById('key-decrypt').classList.add('hidden');
        document.getElementById('hill-matrix-encrypt').classList.remove('hidden');
        document.getElementById('hill-matrix-decrypt').classList.remove('hidden');
        document.getElementById('hill-size-encrypt').classList.remove('hidden');
        document.getElementById('hill-size-decrypt').classList.remove('hidden');

        // Initialize with default 2x2
        document.getElementById('hill-n-enc').value = 2;
        document.getElementById('hill-n-dec').value = 2;
        updateHillMatrixSize('encrypt', 2);
        updateHillMatrixSize('decrypt', 2);
    } else {
        document.getElementById('key-encrypt').classList.remove('hidden');
        document.getElementById('key-decrypt').classList.remove('hidden');
        document.getElementById('hill-matrix-encrypt').classList.add('hidden');
        document.getElementById('hill-matrix-decrypt').classList.add('hidden');
        document.getElementById('hill-size-encrypt').classList.add('hidden');
        document.getElementById('hill-size-decrypt').classList.add('hidden');

        document.getElementById('key-encrypt').placeholder = keyPlaceholders[algorithm];
        document.getElementById('key-decrypt').placeholder = keyPlaceholders[algorithm];
        document.getElementById('key-encrypt').value = keyPlaceholders[algorithm];
        document.getElementById('key-decrypt').value = keyPlaceholders[algorithm];

        // Show Playfair 5x5 matrix visualizer
        if (algorithm === 'playfair') {
            initPlayfairMatrix();
            // Provide a default value if empty to satisfy 'required' attribute and show it works
            if (!document.getElementById('plaintext').value) {
                document.getElementById('plaintext').value = 'PLAYFAIR';
            }
        } else {
            teardownPlayfairMatrix();
        }

        // Ensure message textareas are always visible
        document.getElementById('plaintext').closest('.form-group').style.display = 'block';
        document.getElementById('ciphertext').closest('.form-group').style.display = 'block';
    }
}

/**
 * Update Hill Matrix size and regenerate inputs
 */
function updateHillMatrixSize(type, size) {
    size = parseInt(size);
    if (isNaN(size) || size < 2) return;
    if (size > 8) {
        alert("⚠️ Let's keep it reasonable! Max matrix size is 8x8 for this demo.");
        size = 8;
        document.getElementById(`hill-n-${type === 'encrypt' ? 'enc' : 'dec'}`).value = 8;
    }

    const container = document.getElementById(`hill-matrix-${type}`);
    container.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
    container.innerHTML = '';

    // Default 2x2 matrix values from example
    const default2x2 = [3, 3, 2, 5];
    // Default 3x3 matrix values from example
    const default3x3 = [6, 24, 1, 13, 16, 10, 20, 17, 15];

    let defaults = [];
    if (size === 2) defaults = default2x2;
    else if (size === 3) defaults = default3x3;
    else {
        // Identity-ish matrix for larger sizes to ensure invertibility by default
        for (let i = 0; i < size * size; i++) {
            const row = Math.floor(i / size);
            const col = i % size;
            defaults.push(row === col ? 1 : 0);
        }
    }

    for (let i = 0; i < size * size; i++) {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = `matrix-input hill-m-${type === 'encrypt' ? 'enc' : 'dec'}`;
        input.value = defaults[i] !== undefined ? defaults[i] : 0;
        input.placeholder = `k${Math.floor(i / size) + 1}${i % size + 1}`;
        container.appendChild(input);
    }
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
    const plaintext = document.getElementById('plaintext').value || (currentAlgorithm === 'playfair' ? 'PLAYFAIR' : '');
    let key;
    if (currentAlgorithm === 'hill') {
        const matrixInputs = document.querySelectorAll('.hill-m-enc');
        key = Array.from(matrixInputs).map(input => input.value).join(' ');
    } else {
        key = document.getElementById('key-encrypt').value;
    }

    const receiverId = document.getElementById('receiver').value;

    if (!plaintext.trim() && currentAlgorithm !== 'playfair') {
        alert('⚠️ Please enter a message to encrypt');
        return;
    }

    if (!key || !key.trim()) {
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

            // Lock the algorithm
            lockAlgorithm();

            // Send message if receiver selected
            if (receiverId && receiverId !== '') {
                await sendMessage(receiverId, data.encrypted, key);
            } else {
                alert('✅ Message encrypted successfully!');
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
    const ciphertext = document.getElementById('ciphertext').value || (currentAlgorithm === 'playfair' ? '' : '');
    let key;
    if (currentAlgorithm === 'hill') {
        const matrixInputs = document.querySelectorAll('.hill-m-dec');
        key = Array.from(matrixInputs).map(input => input.value).join(' ');
    } else {
        key = document.getElementById('key-decrypt').value;
    }

    if (!ciphertext.trim() && currentAlgorithm !== 'playfair') {
        alert('⚠️ Please enter an encrypted message to decrypt');
        return;
    }

    if (!key || !key.trim()) {
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

            // Lock the algorithm
            lockAlgorithm();

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

function lockAlgorithm() {
    isLocked = true;
    // Show reset button
    document.getElementById('btn-reset').classList.remove('hidden');
    // Visual feedback for disabled buttons
    document.querySelectorAll('.algorithm-btn').forEach(btn => {
        if (!btn.classList.contains('active')) {
            btn.style.opacity = '0.5';
            btn.style.cursor = 'not-allowed';
        }
    });
}

function resetSession() {
    isLocked = false;
    currentAlgorithm = 'caesar';

    // Reset selection buttons
    document.querySelectorAll('.algorithm-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.opacity = '1';
        btn.style.cursor = 'pointer';
    });
    document.getElementById('btn-caesar').classList.add('active');
    document.getElementById('btn-reset').classList.add('hidden');

    // Clear fields
    document.getElementById('plaintext').value = '';
    document.getElementById('ciphertext').value = '';
    document.getElementById('encrypted-text').textContent = '';
    document.getElementById('decrypted-text').textContent = '';
    document.getElementById('encrypt-result').classList.add('hidden');
    document.getElementById('decrypt-result').classList.add('hidden');

    // Hide Playfair matrix if visible
    teardownPlayfairMatrix();

    // Reset to Caesar defaults
    selectAlgorithm('caesar');

    alert('🔄 Session reset. You can now choose a different algorithm.');
}
