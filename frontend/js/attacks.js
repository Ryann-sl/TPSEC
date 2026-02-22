/**
 * Attacks JavaScript - Concurrent execution supported
 */

// State management for each attack
const attacks = {
    mitm: {
        timer: null,
        initialized: false
    },
    dictionary: {
        timer: null,
        initialized: false
    },
    bruteforce: {
        timer: null,
        initialized: false
    }
};

let mitmState = {
    originalMessage: '',
    algorithm: 'plaintext',
    modifiedMessage: null,
    isIntercepted: false,
    key: null,
    encryptedMessage: ''
};

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;

    // Initialize by showing MITM or none, but elements are now static in HTML
    // We can default to hiding all or showing one. Let's start with none active or MITM.
    // showAttack('mitm'); // Optional: auto-open first one?
});

function showAttack(type) {
    // Hide all interfaces
    document.getElementById('mitm-interface').classList.add('hidden');
    document.getElementById('dictionary-interface').classList.add('hidden');
    document.getElementById('bruteforce-interface').classList.add('hidden');

    // Show the selected one
    const selected = document.getElementById(`${type}-interface`);
    if (selected) {
        selected.classList.remove('hidden');
    }

    // Update active state visuals on cards (optional but good for UX)
    document.querySelectorAll('.attack-card').forEach(card => card.classList.remove('active-card'));
    // We'd need IDs on cards to target them specificially, or just rely on content.
}

// ==================== MITM ATTACK ====================

async function startMITM() {
    mitmState.originalMessage = document.getElementById('mitm-message').value;
    mitmState.algorithm = 'plaintext';
    mitmState.key = null;

    if (!mitmState.originalMessage || !mitmState.originalMessage.trim()) {
        alert('Please enter a message correctly.');
        return;
    }

    mitmState.encryptedMessage = mitmState.originalMessage;

    // Start Animation: Sender -> Attacker
    const packet = document.getElementById('mitm-packet');

    // RESET ANIMATION
    packet.style.animation = 'none';
    packet.offsetHeight; /* trigger reflow */
    packet.style.animation = '';
    packet.style.display = '';

    packet.className = 'packet animating-to-mitm';

    document.getElementById('mitm-results').innerHTML = '<div class="alert alert-info">📡 Transmitting packet...</div>';

    // Wait for animation to reach middle (2s defined in CSS)
    setTimeout(() => {
        showInterceptPanel(mitmState.encryptedMessage);
    }, 2000);
}

function showInterceptPanel(encryptedText) {
    document.getElementById('intercept-panel').classList.remove('hidden');
    document.getElementById('intercepted-text').value = encryptedText;
    document.getElementById('mitm-results').innerHTML = '<div class="alert alert-warning">⚠️ Packet Intercepted by Attacker!</div>';
}

function cancelMITM() {
    document.getElementById('intercept-panel').classList.add('hidden');
    document.getElementById('mitm-packet').style.display = 'none';
    document.getElementById('mitm-results').innerHTML = '<div class="alert alert-error">❌ Packet Dropped. Communication Failed.</div>';
}

async function forwardMessage() {
    const modifiedText = document.getElementById('intercepted-text').value;
    mitmState.modifiedMessage = modifiedText;

    // Hide panel
    document.getElementById('intercept-panel').classList.add('hidden');

    // Resume Animation: Attacker -> Receiver
    const packet = document.getElementById('mitm-packet');
    packet.className = 'packet animating-to-receiver';

    document.getElementById('mitm-results').innerHTML = '<div class="alert alert-info">📡 Forwarding packet to receiver...</div>';

    try {
        const data = await apiRequest('/attack/mitm', {
            method: 'POST',
            body: JSON.stringify({
                encrypted_message: mitmState.encryptedMessage,
                algorithm: mitmState.algorithm,
                modified_message: modifiedText
            })
        });

        // Wait for animation
        setTimeout(() => {
            if (data && data.success) {
                displayTerminalLogs(data.result.logs, 'mitm-results', 'mitm');
            }
        }, 2000);

    } catch (error) {
        document.getElementById('mitm-results').innerHTML = '<div class="alert alert-error">Attack failed</div>';
    }
}


// ==================== DICTIONARY ATTACK ====================

async function runDictionary() {
    const password = document.getElementById('dict-password').value;
    const maxAttempts = parseInt(document.getElementById('dict-attempts').value);
    const fileInput = document.getElementById('dict-file');

    if (!password || !password.trim()) {
        alert("Please enter a target password.");
        return;
    }

    let customWordlist = null;

    if (fileInput.files.length > 0) {
        try {
            const text = await readFile(fileInput.files[0]);
            customWordlist = text.split(/\r?\n/).filter(line => line.trim() !== '');
        } catch (e) {
            alert("Error reading file");
            return;
        }
    }

    const results = document.getElementById('dictionary-results');
    results.innerHTML = '<div class="loading-spinner"></div>';

    // Start specific timer
    startTimer('dictionary');

    try {
        const data = await apiRequest('/attack/dictionary', {
            method: 'POST',
            body: JSON.stringify({
                password,
                max_attempts: maxAttempts,
                wordlist: customWordlist
            })
        });

        if (data && data.success) {
            displayTerminalLogs(data.result.logs, 'dictionary-results', 'dictionary');
        }
    } catch (error) {
        results.innerHTML = '<div class="alert alert-error">Attack failed</div>';
        stopTimer('dictionary');
    }
}

function readFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}


// ==================== BRUTE FORCE ====================

async function runBruteForce() {
    const message = document.getElementById('brute-message').value;
    const results = document.getElementById('bruteforce-results');

    results.innerHTML = '<div class="loading-spinner"></div>';
    startTimer('bruteforce');

    try {
        const data = await apiRequest('/attack/bruteforce', {
            method: 'POST',
            body: JSON.stringify({ ciphertext: message, algorithm: 'caesar' })
        });

        if (data && data.success) {
            displayBruteForceResults(data.result, 'bruteforce-results');
        }
    } catch (error) {
        results.innerHTML = '<div class="alert alert-error">Attack failed</div>';
    } finally {
        stopTimer('bruteforce');
    }
}

// ==================== TERMINAL & UTILS ====================

function displayTerminalLogs(logs, targetId, attackType) {
    const results = document.getElementById(targetId);
    if (!results) return;

    // Stop the processing timer as logs are ready (simulated end of processing)
    if (attackType) stopTimer(attackType);

    let html = `
    <div class="terminal">
        <div class="terminal-controls">
            <div class="terminal-dots">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
            </div>
            <!-- Timer that shows final time or static text -->
            <div class="terminal-timer" id="timer-${attackType}">Done</div>
            <button class="terminal-refresh" onclick="clearResults('${targetId}')">Refresh ↺</button>
        </div>
        <div class="terminal-body">
    `;

    logs.forEach(log => {
        html += `<div class="terminal-line"><span class="text-secondary">[${new Date(log.timestamp * 1000).toLocaleTimeString()}]</span> ${log.message}</div>`;
    });

    html += '</div></div>';
    results.innerHTML = html;
}

function displayBruteForceResults(result, targetId) {
    const results = document.getElementById(targetId);

    let html = `
    <div class="terminal">
        <div class="terminal-controls">
            <div class="terminal-dots">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
            </div>
            <div class="terminal-timer">Done in ${result.attempts * 0.05}s</div>
            <button class="terminal-refresh" onclick="clearResults('${targetId}')">Refresh ↺</button>
        </div>
        <div class="terminal-body">
    `;

    result.logs.forEach(log => {
        html += `<div class="terminal-line">${log.message}</div>`;
    });

    html += '</div></div>';
    results.innerHTML = html;
}

function clearResults(targetId) {
    const results = document.getElementById(targetId);
    if (results) results.innerHTML = '';
}

function startTimer(attackType) {
    if (attacks[attackType].timer) clearInterval(attacks[attackType].timer);

    let startTime = Date.now();
    // Use a small update interval. 
    // Note: We need to inject this timer into the DOM *before* the logs appear if we want to show it LIVE.
    // Currently, `loading-spinner` is shown until the end. 
    // The previous code had a `proc-timer` in the `displayTerminalLogs`, but that was AFTER processing.
    // If we want a live timer, we need a structure that exists during loading.
    // For now, let's just keep the internal state clean.
}

function stopTimer(attackType) {
    if (attacks[attackType] && attacks[attackType].timer) {
        clearInterval(attacks[attackType].timer);
        attacks[attackType].timer = null;
    }
}

