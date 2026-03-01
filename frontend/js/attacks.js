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

function showAttack(type) {
    if (type === 'mitm') {
        alert('Man-in-the-Middle (MiTM) Attack simulation is coming soon!');
        return;
    }

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

    const message = document.getElementById('mitm-message').value;
    const algo = document.getElementById('mitm-algo-select').value;
    const key = document.getElementById('mitm-key').value;

    if (!message) {
        alert('Please enter a message to send.');
        return;
    }

    activeAttack = 'mitm';
    mitmState.originalMessage = message;
    mitmState.algorithm = algo;
    mitmState.key = key;

    let encryptedMessage = message;

    // Perform encryption if needed
    if (algo !== 'plaintext') {
        try {
            const endpoint = `/encrypt/${algo}`;
            const payload = { plaintext: message };
            if (algo === 'caesar') {
                payload.shift = key || 3;
            } else {
                payload.key = key || (algo === 'hill' ? 'HILL' : 'SECRET');
            }

            const data = await apiRequest(endpoint, {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (data && data.success) {
                encryptedMessage = data.encrypted;
            } else {
                throw new Error(data ? data.message : 'Encryption failed');
            }
        } catch (error) {
            alert('Encryption Error: ' + error.message);
            activeAttack = null;
            return;
        }
    }

    mitmState.encryptedMessage = encryptedMessage;

    // UI: Reset decrypt tool preview
    const preview = document.getElementById('mitm-decrypted-preview');
    if (preview) preview.textContent = '';
    const attackerKeyInput = document.getElementById('mitm-attacker-key');
    if (attackerKeyInput) attackerKeyInput.value = '';

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
        showInterceptPanel(encryptedMessage);
    }, 2000);
}

async function mitmAttackerDecrypt() {
    const ciphertext = document.getElementById('intercepted-text').value;
    const key = document.getElementById('mitm-attacker-key').value;
    const algo = mitmState.algorithm;
    const preview = document.getElementById('mitm-decrypted-preview');

    if (algo === 'plaintext') {
        preview.textContent = 'Message is already plaintext.';
        return;
    }

    if (!key) {
        preview.textContent = 'Enter a key to attempt decryption.';
        return;
    }

    try {
        const endpoint = `/decrypt/${algo}`;
        const payload = { ciphertext: ciphertext };
        if (algo === 'caesar') {
            payload.shift = key;
        } else {
            payload.key = key;
        }

        const data = await apiRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        if (data && data.success) {
            preview.innerHTML = `🔓 <span class="text-success">Plaintext:</span> ${data.decrypted}`;
        } else {
            preview.innerHTML = `❌ <span class="text-danger">Failed:</span> ${data.message || 'Invalid key'}`;
        }
    } catch (error) {
        preview.innerHTML = '❌ Error attempting decryption.';
    }
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
                modified_message: modifiedText,
                key: mitmState.key
            })
        });

        // Wait for animation
        setTimeout(() => {
            activeAttack = null;
            if (data && data.success) {
                displayTerminalLogs(data.result.logs, 'mitm-results', 'mitm');
                // Optional: Show what Bob actually sees
                if (data.result.receiver_plaintext) {
                    const results = document.getElementById('mitm-results');
                    results.innerHTML += `
                        <div class="card mt-3" style="border-left: 4px solid var(--neon-cyan); background: rgba(0, 240, 255, 0.05);">
                            <h4 style="color: var(--neon-cyan); margin-bottom: 0.5rem;">📥 Bob (Receiver) Received:</h4>
                            <div style="font-family: 'Fira Code', monospace; padding: 0.75rem; background: rgba(0,0,0,0.2); border-radius: 4px;">
                                ${data.result.receiver_plaintext}
                            </div>
                            <p class="text-secondary mt-2" style="font-size: 0.85rem;">
                                ${data.result.modified_message !== data.result.intercepted_message ?
                            '⚠️ Note: The message was tampered during transit!' :
                            '✅ Message matches the original ciphertext.'}
                            </p>
                        </div>
                    `;
                }
            }
        }, 2000);

    } catch (error) {
        activeAttack = null;
        document.getElementById('mitm-results').innerHTML = '<div class="alert alert-error">Attack failed</div>';
    }
}


// ==================== DICTIONARY ATTACK ====================

let dictSessionId = null; //unique id returned by server to identify attack session
let dictPollIntervalId = null; // polling (time of each server call)
let dictTimerInterval = null; // timer for elapsed time
let dictStartTime = null; // start time of the attack
let dictRenderedLogs = 0; // number of logs rendered
let dictIsPaused = false;  // client-side tracking of pause state

function updateDictModeInfo() {

    document.getElementById('dict-case-info').classList.remove('hidden');
}

async function startDictionary() {
    const password = document.getElementById('dict-password').value;
    const caseId = document.getElementById('dict-case-select').value;
    const fileInput = document.getElementById('dict-file');
    const file = fileInput.files[0];

    if (!password) {
        alert('Please enter a target password to crack.');
        return;
    }

    if (!file) {
        alert('Please implement a file (Wordlist required).');
        return;
    }

    // Read the file content
    let wordlist = [];
    try {
        const content = await readFile(file);
        wordlist = content.split(/\r?\n/).filter(line => line.trim() !== '');

        if (wordlist.length === 0) {
            alert('The provided file is empty or invalid.');
            return;
        }

        // --- CONTENT VALIDATION BASED ON CASE ---
        const firstFew = wordlist.slice(0, 10); // Check a sample
        let isValid = true;
        let errorMsg = '';

        if (caseId === 'case1') {
            // Case 1: 3 chars, ONLY {2, 3, 4}
            const invalid = wordlist.find(w => w.length !== 3 || !/^[234]+$/.test(w));
            if (invalid) {
                isValid = false;
                errorMsg = `Case 1 Mismatch: Found invalid entry "${invalid}".\nExpected: 3 characters using only {2, 3, 4}.`;
            }
        } else if (caseId === 'case2') {
            // Case 2: 5 digits
            const invalid = wordlist.find(w => w.length !== 5 || !/^\d+$/.test(w));
            if (invalid) {
                isValid = false;
                errorMsg = `Case 2 Mismatch: Found invalid entry "${invalid}".\nExpected: Exactly 5 digits (0-9).`;
            }
        } else if (caseId === 'case3') {
            // Case 3: 6 chars mixed
            const invalid = wordlist.find(w => w.length !== 6);
            if (invalid) {
                isValid = false;
                errorMsg = `Case 3 Mismatch: Found invalid entry "${invalid}".\nExpected: Exactly 6 characters.`;
            }
        }

        if (!isValid) {
            alert(`⚠️ WORDLIST ERROR\n\n${errorMsg}\n\nPlease upload the correct file for ${caseId.toUpperCase()} or change the Attack Mode.`);
            return;
        }

    } catch (error) {
        alert('Problem reading the wordlist file: ' + error.message);
        return;
    }

    const payload = {
        password: password,
        case_id: caseId,
        wordlist: wordlist
    };

    // UI Updates
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

    // Start/Reset Local UI Timer
    if (dictTimerInterval) clearInterval(dictTimerInterval);
    dictTimerInterval = setInterval(() => {
        if (dictSessionId && !dictIsPaused && dictStartTime) {
            const sec = ((Date.now() - dictStartTime) / 1000).toFixed(1);
            const el = document.getElementById('dict-elapsed');
            if (el) el.textContent = sec + 's';
        }
    }, 100);

    // Send start request
    let data;
    try {
        data = await apiRequest('/attack/dictionary/start', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    } catch (e) {
        alertDictError('Failed to start attack. Check server connectivity.');
        return;
    }

    if (!data || !data.success) {
        alertDictError(data ? data.message : 'Server error');
        return;
    }

    dictSessionId = data.session_id;

    // Polling loop every 500ms
    if (dictPollIntervalId) clearInterval(dictPollIntervalId);
    dictPollIntervalId = setInterval(async () => {
        try {
            const poll = await apiRequest(`/attack/dictionary/poll/${dictSessionId}`, { method: 'GET' });
            if (!poll || !poll.success) return;

            // Sync elapsed time from server to local start time to avoid drift
            if (poll.elapsed !== undefined) {

                if (!poll.paused) {
                    dictStartTime = Date.now() - (poll.elapsed * 1000);
                } else {
                    // Update display immediately if paused
                    document.getElementById('dict-elapsed').textContent = poll.elapsed.toFixed(1) + 's';
                }
            }

            // Append only new logs
            const termBody = document.getElementById('dictionary-terminal-body');
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
    if (dictPollIntervalId) clearInterval(dictPollIntervalId);
    if (dictTimerInterval) clearInterval(dictTimerInterval);
    dictPollIntervalId = null;
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
            <button class="terminal-refresh" onclick="clearResults('${attackType}-results')">Refresh ↺</button>
        </div>
        <div class="terminal-body" id="${attackType}-terminal-body" style="max-height:320px; overflow-y:auto;"></div>
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

let currentBruteMode = 3; // Default to Mode 3
let bruteAbortController = null;
let bruteIsPaused = false;
let bruteSessionId = null;

function setBruteMode(mode) {
    currentBruteMode = mode;

    // Update button UI
    document.querySelectorAll('[id^="btn-mode-"]').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline');
    });

    const activeBtn = document.getElementById(`btn-mode-${mode}`);
    if (activeBtn) {
        activeBtn.classList.remove('btn-outline');
        activeBtn.classList.add('btn-primary');
    }
}

// Initialize the default active mode button on load
document.addEventListener('DOMContentLoaded', () => {
    setBruteMode(3);
});

async function runBruteForce() {
    if (activeAttack) return;

    const password = document.getElementById('brute-message').value.trim();
    // === Mode config ===
    const modeConfig = {
        3: { length: 3, charset: '234', label: "Mode 3 — exactly 3 chars, only '2', '3', or '4'" },
        5: { length: 5, charset: '0123456789', label: "Mode 5 — exactly 5 chars, only digits (0-9)" },
        6: { length: 6, charset: null, label: "Mode 6 — exactly 6 chars, alphanumeric + special chars" }
    };
    const mode = modeConfig[currentBruteMode];

    // === Length validation ===
    if (password.length !== mode.length) {
        alert(`⚠️ Password length mismatch!\n\n${mode.label}\n\nYou entered ${password.length} character(s). Please enter exactly ${mode.length} character(s).`);
        return;
    }

    // === Character validation ===
    if (mode.charset !== null) {
        const invalidChars = [...password].filter(c => !mode.charset.includes(c));
        if (invalidChars.length > 0) {
            alert(`⚠️ Invalid character(s) detected: [ ${[...new Set(invalidChars)].join(', ')} ]\n\n${mode.label}`);
            return;
        }
    } else {
        // Mode 6: ensure no character is completely outside printable ASCII
        const invalidChars = [...password].filter(c => c.charCodeAt(0) < 32 || c.charCodeAt(0) > 126);
        if (invalidChars.length > 0) {
            alert(`⚠️ Invalid character(s) detected. Mode 6 only allows printable ASCII characters.`);
            return;
        }
    }

    activeAttack = 'bruteforce';

    const results = document.getElementById('bruteforce-results');
    results.innerHTML = buildTerminalShell('bruteforce');

    // Declare at outer scope so catch/finally can access them
    const termBody = results.querySelector('.terminal-body');
    const termTimer = results.querySelector('.terminal-timer');
    termTimer.textContent = 'Running...';

    // Show stop/pause, hide start
    document.getElementById('brute-start-btn').style.display = 'none';
    document.getElementById('brute-pause-btn').style.display = 'inline-flex';
    document.getElementById('brute-pause-btn').textContent = '⏸ Pause';
    document.getElementById('brute-stop-btn').style.display = 'inline-flex';

    bruteIsPaused = false;
    bruteSessionId = null;
    bruteAbortController = new AbortController();

    startTimer('bruteforce');

    function appendLog(text) {
        const div = document.createElement('div');
        div.className = 'terminal-line';
        div.innerHTML = `<span class="text-secondary">[${new Date().toLocaleTimeString()}]</span> ${text}`;
        termBody.appendChild(div);
        termBody.scrollTop = termBody.scrollHeight;
    }

    try {
        const response = await fetch('/api/attack/bruteforce', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ password, algorithm: 'raw', mode: currentBruteMode }),
            signal: bruteAbortController.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete last line

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const event = JSON.parse(line.substring(6));

                    // Read session ID from first SSE event
                    if (event.session_id && !bruteSessionId) {
                        bruteSessionId = event.session_id;
                    }

                    if (event.type === 'done') {
                        termTimer.textContent = `Done in ${Number(event.message.time).toFixed(2)}s`;
                    } else {
                        appendLog(String(event.message));
                    }
                } catch (e) {
                    // Ignore malformed SSE lines
                }
            }
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            appendLog('🛑 ATTACK ABORTED BY USER');
            termTimer.textContent = 'Aborted';
        } else {
            appendLog(`❌ Error: ${error.message}`);
        }
    } finally {
        activeAttack = null;
        bruteAbortController = null;
        stopTimer('bruteforce');

        // Reset buttons
        document.getElementById('brute-start-btn').style.display = 'inline-flex';
        document.getElementById('brute-pause-btn').style.display = 'none';
        document.getElementById('brute-stop-btn').style.display = 'none';
    }
}

async function stopBruteForce() {
    if (bruteAbortController) {
        bruteAbortController.abort();
    }
    if (bruteSessionId) {
        fetch(`/api/attack/bruteforce/stop/${bruteSessionId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }).catch(() => { });
    }
}

async function togglePauseBruteForce() {
    bruteIsPaused = !bruteIsPaused;
    const pauseBtn = document.getElementById('brute-pause-btn');

    if (bruteIsPaused) {
        pauseBtn.textContent = '▶ Resume';
        if (bruteSessionId) {
            fetch(`/api/attack/bruteforce/pause/${bruteSessionId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            }).catch(() => { });
        }
    } else {
        pauseBtn.textContent = '⏸ Pause';
        if (bruteSessionId) {
            fetch(`/api/attack/bruteforce/resume/${bruteSessionId}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            }).catch(() => { });
        }
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

