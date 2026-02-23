/**
 * Playfair Cipher – 5×5 Matrix Visualizer
 * Hooks into the encrypt keyword input to fetch and render the key matrix live.
 */

let playfairDebounceTimer = null;

/**
 * Show the Playfair matrix section and start listening to the keyword input.
 */
function initPlayfairMatrix() {
    // Show the matrix section when Playfair is selected
    const matrixSection = document.getElementById('playfair-matrix-section');
    if (matrixSection) {
        matrixSection.style.display = 'block';
    }

    const keyInput = document.getElementById('key-encrypt');
    if (keyInput) {
        // Render immediately with current value
        fetchAndRenderMatrix(keyInput.value || 'SECRET');

        // Re-render on every keystroke
        keyInput.addEventListener('input', onPlayfairKeywordChange);
    }
}

/**
 * Hide the Playfair matrix section and remove the listener.
 */
function teardownPlayfairMatrix() {
    const matrixSection = document.getElementById('playfair-matrix-section');
    if (matrixSection) {
        matrixSection.style.display = 'none';
    }
    const keyInput = document.getElementById('key-encrypt');
    if (keyInput) {
        keyInput.removeEventListener('input', onPlayfairKeywordChange);
    }
}

function onPlayfairKeywordChange(e) {
    clearTimeout(playfairDebounceTimer);
    playfairDebounceTimer = setTimeout(() => {
        fetchAndRenderMatrix(e.target.value || 'SECRET');
    }, 300);
}

/**
 * Fetch 5×5 matrix from backend and render it in the grid.
 */
async function fetchAndRenderMatrix(keyword) {
    if (!keyword.trim()) return;

    try {
        const token = localStorage.getItem('token') || '';
        const resp = await fetch(`/api/playfair/matrix?keyword=${encodeURIComponent(keyword)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await resp.json();

        if (data.success) {
            renderPlayfairGrid(data.matrix, keyword.toUpperCase().replace(/J/g, 'I').replace(/[^A-Z]/g, ''));
        }
    } catch (err) {
        console.error('Failed to fetch Playfair matrix:', err);
    }
}

/**
 * Render the 5×5 matrix into the grid div.
 * Highlight cells that come from the keyword letters.
 */
function renderPlayfairGrid(matrix, cleanKeyword) {
    const grid = document.getElementById('playfair-grid');
    grid.innerHTML = '';

    // Deduplicate keyword chars to know which letters are "keyword" cells
    const kwChars = new Set();
    for (const ch of cleanKeyword) {
        if (kwChars.size < 25) kwChars.add(ch);
    }

    for (let r = 0; r < 5; r++) {
        for (let c = 0; c < 5; c++) {
            const letter = matrix[r][c];
            const cell = document.createElement('div');
            cell.className = 'playfair-cell' + (kwChars.has(letter) ? ' highlight' : '');
            cell.textContent = letter;
            cell.title = `Row ${r + 1}, Col ${c + 1}`;
            grid.appendChild(cell);
        }
    }
}
