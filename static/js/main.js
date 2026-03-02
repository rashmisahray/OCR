/**
 * Nova OCR - Core Frontend Logic
 * Refactored for better performance and modularity.
 */

class NovaOCR {
    constructor() {
        // Essential DOM Elements
        this.dropZone = document.getElementById('drop-zone');
        this.fileInput = document.getElementById('file-input');
        this.previewContainer = document.getElementById('preview-container');
        this.imagePreview = document.getElementById('image-preview');
        this.removeBtn = document.getElementById('remove-img');
        this.extractBtn = document.getElementById('extract-btn');
        this.resultSection = document.getElementById('result-section');
        this.outputText = document.getElementById('output-text');
        this.copyBtn = document.getElementById('copy-btn');
        this.downloadBtn = document.getElementById('download-btn');
        this.loader = document.querySelector('.btn-loader');
        this.btnText = document.querySelector('.nova-btn .text');

        this.selectedFile = null;
        this.initEvents();
    }

    initEvents() {
        // File Selection
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and Drop
        ['dragenter', 'dragover'].forEach(name => {
            this.dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                this.dropZone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(name => {
            this.dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                this.dropZone.classList.remove('dragover');
            });
        });

        this.dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) this.handleFileSelect({ target: { files } });
        });

        // Actions
        this.removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.resetUpload();
        });

        this.extractBtn.addEventListener('click', () => this.processOCR());

        this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        this.downloadBtn.addEventListener('click', () => this.downloadResult());
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            this.selectedFile = file;
            this.showPreview(file);
            this.extractBtn.disabled = false;
        }
    }

    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.imagePreview.src = e.target.result;
            this.previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    resetUpload() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.imagePreview.src = '';
        this.previewContainer.classList.add('hidden');
        this.extractBtn.disabled = true;
        this.resultSection.classList.add('hidden');
    }

    async processOCR() {
        if (!this.selectedFile) return;

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        // UI State: Loading
        this.setLoading(true);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                this.displayResult(data.text);
            } else {
                alert(`Analysis Error: ${data.error}`);
            }
        } catch (error) {
            alert('System Failure: Connection lost to processing core.');
            console.error(error);
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(isLoading) {
        this.extractBtn.disabled = isLoading;
        if (isLoading) {
            this.loader.classList.remove('hidden');
            this.btnText.textContent = 'Processing...';
        } else {
            this.loader.classList.add('hidden');
            this.btnText.textContent = 'Extract Intelligence';
        }
    }

    displayResult(text) {
        this.outputText.value = text;
        this.resultSection.classList.remove('hidden');
        this.resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    copyToClipboard() {
        this.outputText.select();
        document.execCommand('copy');

        // Brief feedback
        const originalIcon = this.copyBtn.innerHTML;
        this.copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
        this.copyBtn.style.color = 'var(--accent-primary)';
        setTimeout(() => {
            this.copyBtn.innerHTML = originalIcon;
            this.copyBtn.style.color = '';
        }, 2000);
    }

    downloadResult() {
        const text = this.outputText.value;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `NovaOCR_Export_${Date.now()}.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
}

// Initialize on Boot
document.addEventListener('DOMContentLoaded', () => {
    window.novaApp = new NovaOCR();
});
