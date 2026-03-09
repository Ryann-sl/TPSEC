// Steganography Module JavaScript - Multi-Media Support
class MultiMediaSteganography {
    constructor() {
        this.token = localStorage.getItem('token');
        if (!this.token) {
            window.location.href = 'index.html';
            return;
        }
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Tab switching
        window.switchTab = (tabName) => {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.getAttribute('onclick').includes(tabName));
            if (activeBtn) activeBtn.classList.add('active');

            const activeTab = document.getElementById(`${tabName}-tab`);
            if (activeTab) activeTab.classList.add('active');
        };

        // Form Submissions
        const mediaTypes = ['image', 'audio', 'video'];
        mediaTypes.forEach(type => {
            const encodeForm = document.getElementById(`${type}-encode-form`);
            if (encodeForm) {
                encodeForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleEncode(type);
                });
            }

            const decodeForm = document.getElementById(`${type}-decode-form`);
            if (decodeForm) {
                decodeForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleDecode(type);
                });
            }
        });
    }

    async handleEncode(type) {
        const fileInput = document.getElementById(`${type}-input`);
        const messageInput = document.getElementById(`${type}-message`);
        const resultBox = document.getElementById(`${type}-result`);

        if (!fileInput.files[0] || !messageInput.value) {
            alert('Please select a file and enter a message.');
            return;
        }

        let fileToUpload = fileInput.files[0];

        // Automatic conversion for Audio
        if (type === 'audio' && !fileToUpload.name.toLowerCase().endsWith('.wav')) {
            this.showResult(type, 'Converting audio to WAV for processing...', null);
            try {
                fileToUpload = await this.convertToWav(fileToUpload);
            } catch (error) {
                this.showResult(type, 'Conversion failed: ' + error.message, null, true);
                return;
            }
        }

        const formData = new FormData();
        formData.append(type, fileToUpload);
        formData.append('message', messageInput.value);

        try {
            const endpoint = `/api/steganography${type === 'image' ? '' : '/' + type}/encode`;
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` },
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.showResult(type, 'Encoded successfully!', result);
            } else {
                this.showResult(type, 'Error: ' + (result.error || result.message), null, true);
            }
        } catch (error) {
            this.showResult(type, 'Network error: ' + error.message, null, true);
        }
    }

    async handleDecode(type) {
        const fileInput = document.getElementById(`${type}-decode-input`);
        const resultBox = document.getElementById(`${type}-result`);

        if (!fileInput.files[0]) {
            alert('Please select a file to decode.');
            return;
        }

        let fileToUpload = fileInput.files[0];

        // Automatic conversion for Audio decode (if needed, though LSB only works on the exact bits)
        // However, if the user uploads a compressed file for decoding, LSB is likely lost.
        // We'll try to convert anyway just to allow the backend to read it.
        if (type === 'audio' && !fileToUpload.name.toLowerCase().endsWith('.wav')) {
            this.showResult(type, 'Attempting to read non-WAV file (Warning: LSB data is likely lost)...', null);
            try {
                fileToUpload = await this.convertToWav(fileToUpload);
            } catch (error) {
                this.showResult(type, 'Read failed: ' + error.message, null, true);
                return;
            }
        }

        const formData = new FormData();
        formData.append(type, fileToUpload);

        try {
            const endpoint = `/api/steganography${type === 'image' ? '' : '/' + type}/decode`;
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` },
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.showResult(type, 'Decoded Message: ' + result.message, result);
            } else {
                this.showResult(type, 'Error: ' + (result.error || result.message), null, true);
            }
        } catch (error) {
            this.showResult(type, 'Network error: ' + error.message, null, true);
        }
    }

    async convertToWav(file) {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const arrayBuffer = await file.arrayBuffer();
        const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

        const wavBlob = this.audioBufferToWav(audioBuffer);
        return new File([wavBlob], file.name.replace(/\.[^/.]+$/, "") + ".wav", { type: 'audio/wav' });
    }

    audioBufferToWav(buffer) {
        const numOfChan = buffer.numberOfChannels;
        const length = buffer.length * numOfChan * 2 + 44;
        const outBuffer = new ArrayBuffer(length);
        const view = new DataView(outBuffer);
        const channels = [];
        let i, sample, offset = 0, pos = 0;

        // write RIFF identifier
        setUint32(0x46464952);                         // "RIFF"
        setUint32(length - 8);                         // file length
        setUint32(0x45564157);                         // "WAVE"

        // write format chunk identifier
        setUint32(0x20746d66);                         // "fmt "
        setUint32(16);                                 // format chunk length
        setUint16(1);                                  // sample format (raw)
        setUint16(numOfChan);
        setUint32(buffer.sampleRate);
        setUint32(buffer.sampleRate * 2 * numOfChan); // byte rate (sample rate * block align)
        setUint16(numOfChan * 2);                     // block align (number of channels * bytes per sample)
        setUint16(16);                                 // bits per sample

        // write data chunk identifier
        setUint32(0x61746164);                         // "data"
        setUint32(length - pos - 4);                   // data chunk length

        for (i = 0; i < buffer.numberOfChannels; i++)
            channels.push(buffer.getChannelData(i));

        while (pos < length) {
            for (i = 0; i < numOfChan; i++) {             // interleave channels
                sample = Math.max(-1, Math.min(1, channels[i][offset])); // clamp
                sample = (sample < 0 ? sample * 0x8000 : sample * 0x7FFF); // scale
                view.setInt16(pos, sample, true);          // write 16nd-bit sample
                pos += 2;
            }
            offset++;
        }

        return new Blob([outBuffer], { type: "audio/wav" });

        function setUint16(data) {
            view.setUint16(pos, data, true);
            pos += 2;
        }

        function setUint32(data) {
            view.setUint32(pos, data, true);
            pos += 4;
        }
    }

    showResult(type, message, data, isError = false) {
        const resultBox = document.getElementById(`${type}-result`);
        resultBox.style.display = 'block';
        resultBox.className = 'result-box ' + (isError ? 'error' : 'success');
        resultBox.innerHTML = `<strong>${message}</strong>`;

        if (data) {
            if (data.encoded_image) this.addDownloadLink(resultBox, data.encoded_image, 'encoded_image.png');
            if (data.encoded_audio) this.addDownloadLink(resultBox, data.encoded_audio, 'encoded_audio.wav');
            if (data.encoded_video) this.addDownloadLink(resultBox, data.encoded_video, 'encoded_video.avi');
        }
    }

    addDownloadLink(container, b64Data, filename) {
        // Convert base64 to Blob for more reliable downloads (especially for large videos)
        const byteCharacters = atob(b64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.className = 'btn btn-success';
        link.style.marginTop = '10px';
        link.innerHTML = 'Download Result';

        // Clean up the URL object after download starts
        link.onclick = () => {
            setTimeout(() => URL.revokeObjectURL(url), 100);
        };

        container.appendChild(document.createElement('br'));
        container.appendChild(link);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.stegoApp = new MultiMediaSteganography();
});
