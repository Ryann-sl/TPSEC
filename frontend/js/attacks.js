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

let activeAttack = null; // | 'mitm' | 'dictionary' | 'bruteforce'

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

});

function showAttack(type) {
    // Prevent switching if an attack is already running
    if (activeAttack && activeAttack !== type) {
        alert(`⚠️ An attack (${activeAttack.toUpperCase()}) is currently in progress. Please stop or finish it before switching.`);
        return;
    }

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
}

// ==================== MITM ATTACK ====================

async function startMITM() {
    if (activeAttack) return;
    activeAttack = 'mitm';

    mitmState.originalMessage = document.getElementById('mitm-message').value;
    mitmState.algorithm = 'plaintext';

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
    activeAttack = null;
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
            activeAttack = null;
            if (data && data.success) {
                displayTerminalLogs(data.result.logs, 'mitm-results', 'mitm');
            }
        }, 2000);

    } catch (error) {
        activeAttack = null;
        document.getElementById('mitm-results').innerHTML = '<div class="alert alert-error">Attack failed</div>';
    }
}


// ==================== DICTIONARY ATTACK ====================

let dictSessionId = null;
let dictPollInterval = null;
let dictTimerInterval = null;
let dictStartTime = null;
let dictRenderedLogs = 0;
let dictIsPaused = false;  // client-side tracking of pause state

async function startDictionary() {
    const password = document.getElementById('dict-password').value.trim();
    const fileInput = document.getElementById('dict-file');

    if (!password) {
        alert("Please enter a target password.");
        return;
    }
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Please upload a wordlist .txt file.");
        return;
    }

    // Read the file
    let wordlist;
    try {
        const text = await readFile(fileInput.files[0]);
        wordlist = text.split(/\r?\n/).filter(line => line.trim() !== '');
    } catch (e) {
        alert("Error reading file.");
        return;
    }

    if (wordlist.length === 0) {
        alert("The wordlist file is empty.");
        return;
    }

    // Clear previous analysis card
    const oldAnalysis = document.getElementById('dict-strength-analysis');
    if (oldAnalysis) oldAnalysis.remove();

    dictRenderedLogs = 0;
    dictStartTime = Date.now();
    activeAttack = 'dictionary';
    dictIsPaused = false;
    document.getElementById('dict-start-btn').style.display = 'none';
    document.getElementById('dict-pause-btn').style.display = 'inline-flex';
    document.getElementById('dict-pause-btn').textContent = '⏸ Pause';
    document.getElementById('dict-stop-btn').style.display = 'inline-flex';
    document.getElementById('dict-status-bar').style.display = 'block';
    document.getElementById('dict-progress-text').textContent = `0 / ${wordlist.length}`;
    document.getElementById('dict-progress-bar').style.width = '0%';
    document.getElementById('dict-elapsed').textContent = '0.0s';
    document.getElementById('dictionary-results').innerHTML = buildTerminalShell('dictionary');

    // Elapsed timer (client-side, ticks every 100ms)
    clearInterval(dictTimerInterval);
    dictTimerInterval = setInterval(() => {
        if (dictSessionId && !dictIsPaused && dictStartTime) {
            const sec = ((Date.now() - dictStartTime) / 1000).toFixed(1);
            document.getElementById('dict-elapsed').textContent = sec + 's';
        }
    }, 100);

    // Send start request
    let data;
    try {
        data = await apiRequest('/attack/dictionary/start', {
            method: 'POST',
            body: JSON.stringify({ password, wordlist })
        });
    } catch (e) {
        alertDictError('Failed to start attack. Check server.');
        return;
    }

    if (!data || !data.success) {
        alertDictError(data ? data.message : 'Server error');
        return;
    }

    dictSessionId = data.session_id;

    // Polling loop every 500ms
    clearInterval(dictPollInterval);
    dictPollInterval = setInterval(async () => {
        try {
            const poll = await apiRequest(`/attack/dictionary/poll/${dictSessionId}`, { method: 'GET' });
            if (!poll || !poll.success) return;

            // Sync elapsed time from server to local start time to avoid drift
            if (poll.elapsed !== undefined) {
                // Adjust dictStartTime so (Date.now() - dictStartTime) equals poll.elapsed
                // Only if not paused (when paused, the interval does nothing anyway)
                if (!poll.paused) {
                    dictStartTime = Date.now() - (poll.elapsed * 1000);
                } else {
                    // Update display immediately if paused
                    document.getElementById('dict-elapsed').textContent = poll.elapsed.toFixed(1) + 's';
                }
            }

            // Append only new logs
            const termBody = document.getElementById('dict-terminal-body');
            if (termBody) {
                const newLogs = poll.logs.slice(dictRenderedLogs);
                newLogs.forEach(log => {
                    const line = document.createElement('div');
                    line.className = 'terminal-line';
                    line.innerHTML = `<span class="text-secondary">[${new Date(log.timestamp * 1000).toLocaleTimeString()}]</span> ${log.message}`;
                    termBody.appendChild(line);
                    termBody.scrollTop = termBody.scrollHeight;
                });
                dictRenderedLogs = poll.logs.length;
            }

            // Update progress
            const pct = poll.total > 0 ? Math.min(100, Math.round((poll.attempts / poll.total) * 100)) : 0;
            document.getElementById('dict-progress-text').textContent = `${poll.attempts} / ${poll.total}`;
            document.getElementById('dict-progress-bar').style.width = pct + '%';

            // Reflect pause state visually
            if (poll.paused && !dictIsPaused) {
                dictIsPaused = true;
                document.getElementById('dict-pause-btn').textContent = '▶ Resume';
                const timerEl = document.getElementById('dict-elapsed');
                if (timerEl) timerEl.style.opacity = '0.45';
            } else if (!poll.paused && dictIsPaused) {
                dictIsPaused = false;
                document.getElementById('dict-pause-btn').textContent = '⏸ Pause';
                const timerEl = document.getElementById('dict-elapsed');
                if (timerEl) timerEl.style.opacity = '1';
            }

            if (poll.done || poll.stopped) {
                finishDictionary(poll);
            }
        } catch (e) { /* ignore transient poll errors */ }
    }, 500);
}

// Update the timer interval to respect paused state
clearInterval(dictTimerInterval);
dictTimerInterval = setInterval(() => {
    if (dictSessionId && !dictIsPaused && dictStartTime) {
        const sec = ((Date.now() - dictStartTime) / 1000).toFixed(1);
        const el = document.getElementById('dict-elapsed');
        if (el) el.textContent = sec + 's';
    }
}, 100);

function stopDictionary() {
    if (dictSessionId) {
        activeAttack = null;
        apiRequest(`/attack/dictionary/stop/${dictSessionId}`, { method: 'POST' }).catch(() => { });
    }
}

function togglePauseDictionary() {
    if (!dictSessionId) return;
    if (dictIsPaused) {
        apiRequest(`/attack/dictionary/resume/${dictSessionId}`, { method: 'POST' }).catch(() => { });
    } else {
        apiRequest(`/attack/dictionary/pause/${dictSessionId}`, { method: 'POST' }).catch(() => { });
    }
}

async function finishDictionary(poll) {
    activeAttack = null;
    clearInterval(dictPollInterval);
    clearInterval(dictTimerInterval);
    dictPollInterval = null;
    dictTimerInterval = null;

    // Final elapsed from server
    const finalElapsed = poll.elapsed ? poll.elapsed.toFixed(2) + 's' : 'done';
    const timerEl = document.getElementById('dict-elapsed');
    if (timerEl) timerEl.textContent = finalElapsed;

    document.getElementById('dict-start-btn').style.display = 'inline-flex';
    document.getElementById('dict-pause-btn').style.display = 'none';
    document.getElementById('dict-stop-btn').style.display = 'none';
    const elEl = document.getElementById('dict-elapsed');
    if (elEl) elEl.style.opacity = '1';

    // Fetch and display strength analysis
    const password = document.getElementById('dict-password').value.trim();
    if (password) {
        try {
            const data = await apiRequest('/password/strength', {
                method: 'POST',
                body: JSON.stringify({ password })
            });
            if (data && data.success) {
                renderStrengthAnalysis(data.result);
            }
        } catch (e) { console.error("Strength analysis failed:", e); }
    }
}

function renderStrengthAnalysis(result) {
    const resultsArea = document.getElementById('dictionary-results');
    if (!resultsArea) return;

    // Create container for analysis if it doesn't exist
    let analysisDiv = document.getElementById('dict-strength-analysis');
    if (!analysisDiv) {
        analysisDiv = document.createElement('div');
        analysisDiv.id = 'dict-strength-analysis';
        analysisDiv.className = 'mt-3 animate-fade-in';
        resultsArea.appendChild(analysisDiv);
    }

    const scoreColor = result.score >= 5 ? '#00ff9d' : (result.score >= 3 ? '#f0a500' : '#ff4d4d');
    const badgeClass = result.strength === 'STRONG' ? 'badge-success' : (result.strength === 'MEDIUM' ? 'badge-warning' : 'badge-error');

    analysisDiv.innerHTML = `
        <div class="card" style="border-left: 4px solid ${scoreColor}; background: rgba(255, 255, 255, 0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.1rem;">🛡️ Password Strength Analysis</h3>
                <div style="font-size: 1.2rem; font-weight: bold; color: ${scoreColor}">
                    Score: ${result.score} / ${result.max_score}
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <span class="badge ${badgeClass}">${result.strength}</span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.5rem;">
                ${result.feedback.map(item => `
                    <div style="font-size: 0.9rem; padding: 0.4rem; border-radius: 4px; background: rgba(255, 255, 255, 0.05);">
                        ${item}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function alertDictError(msg) {
    activeAttack = null;
    clearInterval(dictTimerInterval);
    clearInterval(dictPollInterval);
    document.getElementById('dict-start-btn').style.display = 'inline-flex';
    document.getElementById('dict-pause-btn').style.display = 'none';
    document.getElementById('dict-stop-btn').style.display = 'none';
    document.getElementById('dict-status-bar').style.display = 'none';
    document.getElementById('dictionary-results').innerHTML = `<div class="alert alert-error">❌ ${msg}</div>`;
}

/** Build an empty terminal shell and return its HTML; also holds a live body div */
function buildTerminalShell(attackType) {
    return `
    <div class="terminal">
        <div class="terminal-controls">
            <div class="terminal-dots">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
            </div>
            <div class="terminal-timer" id="timer-${attackType}">Running...</div>
            <button class="terminal-refresh" onclick="clearResults('dictionary-results')">Refresh ↺</button>
        </div>
        <div class="terminal-body" id="dict-terminal-body" style="max-height:320px; overflow-y:auto;"></div>
    </div>`;
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
    if (activeAttack) return;
    activeAttack = 'bruteforce';

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
        activeAttack = null;
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
}

function stopTimer(attackType) {
    if (attacks[attackType] && attacks[attackType].timer) {
        clearInterval(attacks[attackType].timer);
        attacks[attackType].timer = null;
    }
}

