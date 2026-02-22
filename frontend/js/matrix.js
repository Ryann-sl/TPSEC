/**
 * Matrix Rain Effect
 * High-performance, cyberpunk-themed matrix rain
 */

document.addEventListener('DOMContentLoaded', () => {
    initMatrixRain();
});

function initMatrixRain() {
    // Create Canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'matrix-bg';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.15'; // Subtle background
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    // Set dimensions
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    // Characters (Katakana + Latin + nums)
    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
    const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const nums = '0123456789';
    const alphabet = katakana + latin + nums;

    const fontSize = 16;
    const columns = width / fontSize;

    // Array of drops - one per column
    const drops = [];
    for (let x = 0; x < columns; x++) {
        drops[x] = 1;
    }

    // Color controls
    let hue = 0;

    function draw() {
        // Black BG for the trail effect
        ctx.fillStyle = 'rgba(10, 14, 39, 0.05)'; // Using bg-primary color with low opacity for trails
        ctx.fillRect(0, 0, width, height);

        // Text style
        ctx.font = fontSize + 'px monospace';

        // Cyberpunk Color Cycle (Cyan -> Magenta -> Green-ish)
        // We'll oscillate hue or just linear cycle
        hue = (hue + 1) % 360;

        // Loop over drops
        for (let i = 0; i < drops.length; i++) {
            // Random character
            const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));

            // Dynamic Color based on position or time
            // Head of the drop is bright white/colored
            // Trail is gradient

            const color1 = `hsl(${hue}, 100%, 50%)`;
            const color2 = `hsl(${hue + 180}, 100%, 50%)`;

            ctx.fillStyle = color1;

            // Draw
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Reset drop to top randomly after it has crossed screen
            if (drops[i] * fontSize > height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            // Increment Y coordinate
            drops[i]++;
        }
    }

    // Resize handler
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    // Loop
    setInterval(draw, 33);
}
