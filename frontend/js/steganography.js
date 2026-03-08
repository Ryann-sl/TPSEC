// Steganography Module JavaScript
class SteganographyApp {
    constructor() {
        this.token = localStorage.getItem('token');
        this.encodedImageData = null;
        
        // Check authentication before initializing
        if (!this.token) {
            this.redirectToLogin();
            return;
        }
        
        this.init();
    }

    redirectToLogin() {
        window.location.href = 'index.html';
    }

    init() {
        this.setupEventListeners();
        this.setupFileUploads();
        this.setupMessageCounter();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.switchTab(tab);
            });
        });

        // Form submissions
        document.getElementById('encode-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.encodeMessage();
        });

        document.getElementById('decode-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.decodeMessage();
        });

        document.getElementById('analyze-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeImage();
        });

        // Logout
        document.querySelector('.logout-btn').addEventListener('click', () => {
            this.logout();
        });
    }

    setupFileUploads() {
        // Encode image upload
        const encodeInput = document.getElementById('encode-image');
        const encodeArea = document.getElementById('encode-file-area');
        
        encodeInput.addEventListener('change', (e) => {
            this.handleFileSelect(e, 'encode');
        });

        this.setupDragAndDrop(encodeArea, encodeInput, 'encode');

        // Decode image upload
        const decodeInput = document.getElementById('decode-image');
        const decodeArea = document.getElementById('decode-file-area');
        
        decodeInput.addEventListener('change', (e) => {
            this.handleFileSelect(e, 'decode');
        });

        this.setupDragAndDrop(decodeArea, decodeInput, 'decode');

        // Analyze image upload
        const analyzeInput = document.getElementById('analyze-image');
        const analyzeArea = document.getElementById('analyze-file-area');
        
        analyzeInput.addEventListener('change', (e) => {
            this.handleFileSelect(e, 'analyze');
        });

        this.setupDragAndDrop(analyzeArea, analyzeInput, 'analyze');
    }

    setupDragAndDrop(area, input, type) {
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.handleFileSelect({ target: { files } }, type);
            }
        });
    }

    setupMessageCounter() {
        const messageTextarea = document.getElementById('encode-message');
        const counter = document.getElementById('message-length');
        
        messageTextarea.addEventListener('input', (e) => {
            const length = e.target.value.length;
            counter.textContent = length;
            
            if (length > 1000) {
                counter.style.color = '#ff4444';
            } else if (length > 800) {
                counter.style.color = '#ffaa00';
            } else {
                counter.style.color = '#00ff88';
            }
        });
    }

    handleFileSelect(event, type) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showNotification('Please select an image file', 'error');
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('File size must be less than 10MB', 'error');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.showImagePreview(e.target.result, type);
        };
        reader.readAsDataURL(file);
    }

    showImagePreview(imageSrc, type) {
        const preview = document.getElementById(`${type}-preview`);
        const img = document.getElementById(`${type}-preview-img`);
        
        img.src = imageSrc;
        preview.style.display = 'block';
        
        // Hide file upload area
        document.getElementById(`${type}-file-area`).style.display = 'none';
    }

    removeImagePreview(type) {
        const preview = document.getElementById(`${type}-preview`);
        const fileArea = document.getElementById(`${type}-file-area`);
        const input = document.getElementById(`${type}-image`);
        
        preview.style.display = 'none';
        fileArea.style.display = 'block';
        input.value = '';
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    async encodeMessage() {
        const fileInput = document.getElementById('encode-image');
        const message = document.getElementById('encode-message').value;

        if (!fileInput.files[0]) {
            this.showNotification('Please select an image', 'error');
            return;
        }

        if (!message.trim()) {
            this.showNotification('Please enter a message', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('message', message);

            const response = await fetch('/api/steganography/encode', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            // Check for unauthorized
            if (response.status === 401) {
                this.showNotification('Session expired. Please log in again.', 'error');
                this.redirectToLogin();
                return;
            }

            let result;
            try {
                result = await response.json();
            } catch (e) {
                this.showNotification('Invalid server response. Please try again.', 'error');
                return;
            }

            if (response.ok && result.success) {
                this.showEncodeResult(result);
                this.encodedImageData = result.encoded_image;
            } else {
                this.showNotification(result.error || 'Encoding failed', 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showEncodeResult(result) {
        const resultSection = document.getElementById('encode-result');
        
        // Update stats
        document.getElementById('result-image-size').textContent = result.image_size;
        document.getElementById('result-message-length').textContent = result.message_length + ' characters';
        document.getElementById('result-capacity').textContent = result.capacity_used;

        // Show encoded image
        const resultImage = document.getElementById('result-image');
        resultImage.src = `data:image/png;base64,${result.encoded_image}`;

        resultSection.style.display = 'block';
        this.showNotification('Message hidden successfully!', 'success');
    }

    async decodeMessage() {
        const fileInput = document.getElementById('decode-image');

        if (!fileInput.files[0]) {
            this.showNotification('Please select an image', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            const response = await fetch('/api/steganography/decode', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            // Check for unauthorized
            if (response.status === 401) {
                this.showNotification('Session expired. Please log in again.', 'error');
                this.redirectToLogin();
                return;
            }

            let result;
            try {
                result = await response.json();
            } catch (e) {
                this.showNotification('Invalid server response. Please try again.', 'error');
                return;
            }

            if (response.ok && result.success) {
                this.showDecodeResult(result);
            } else {
                this.showNotification(result.error || 'No hidden message found', 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showDecodeResult(result) {
        const resultSection = document.getElementById('decode-result');
        
        // Update stats
        document.getElementById('decode-bits').textContent = result.bits_extracted;

        // Show extracted message
        const messageDiv = document.getElementById('extracted-message');
        messageDiv.textContent = result.message;
        if (result.note) {
            messageDiv.innerHTML += `<br><small><em>${result.note}</em></small>`;
        }

        resultSection.style.display = 'block';
        this.showNotification('Message extracted successfully!', 'success');
    }

    async analyzeImage() {
        const fileInput = document.getElementById('analyze-image');

        if (!fileInput.files[0]) {
            this.showNotification('Please select an image', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            const response = await fetch('/api/steganography/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            // Check for unauthorized
            if (response.status === 401) {
                this.showNotification('Session expired. Please log in again.', 'error');
                this.redirectToLogin();
                return;
            }

            let result;
            try {
                result = await response.json();
            } catch (e) {
                this.showNotification('Invalid server response. Please try again.', 'error');
                return;
            }

            if (response.ok && result.success) {
                this.showAnalyzeResult(result);
            } else {
                this.showNotification(result.error || 'Analysis failed', 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showAnalyzeResult(result) {
        const resultSection = document.getElementById('analyze-result');
        
        // Update image info
        document.getElementById('analysis-size').textContent = result.image_info.size;
        document.getElementById('analysis-pixels').textContent = result.image_info.pixels.toLocaleString();
        document.getElementById('analysis-mode').textContent = result.image_info.mode;

        // Update capacity info
        document.getElementById('analysis-max-bits').textContent = result.capacity.max_bits.toLocaleString() + ' bits';
        document.getElementById('analysis-max-chars').textContent = result.capacity.max_characters.toLocaleString() + ' chars';
        document.getElementById('analysis-used').textContent = result.capacity.used_percentage + '%';

        // Update detection result
        const statusDiv = document.getElementById('detection-status');
        const hasMessage = result.analysis.has_potential_message;
        
        if (hasMessage) {
            statusDiv.innerHTML = `
                <span class="status-icon">⚠️</span>
                <span class="status-text">Potential hidden message detected</span>
            `;
            statusDiv.className = 'detection-status warning';
        } else {
            statusDiv.innerHTML = `
                <span class="status-icon">✅</span>
                <span class="status-text">No obvious signs of steganography</span>
            `;
            statusDiv.className = 'detection-status safe';
        }

        // Show sample bits
        const sampleBitsDiv = document.getElementById('sample-bits');
        const sampleBitsCode = document.getElementById('sample-bits-code');
        sampleBitsCode.textContent = result.analysis.sample_bits;
        sampleBitsDiv.style.display = 'block';

        resultSection.style.display = 'block';
        this.showNotification('Image analysis complete!', 'success');
    }

    downloadEncodedImage() {
        if (!this.encodedImageData) {
            this.showNotification('No encoded image available', 'error');
            return;
        }

        const link = document.createElement('a');
        link.href = `data:image/png;base64,${this.encodedImageData}`;
        link.download = 'steganography_encoded.png';
        link.click();
        
        this.showNotification('Image downloaded!', 'success');
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    }
}

// Helper functions for global access
function switchTab(tabName) {
    app.switchTab(tabName);
}

function removeEncodeImage() {
    app.removeImagePreview('encode');
}

function removeDecodeImage() {
    app.removeImagePreview('decode');
}

function removeAnalyzeImage() {
    app.removeImagePreview('analyze');
}

function downloadEncodedImage() {
    app.downloadEncodedImage();
}

function logout() {
    app.logout();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Initialize app
    window.app = new SteganographyApp();
});
