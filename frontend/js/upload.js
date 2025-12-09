/**
 * TranscribeAI - Upload & Recording Module
 * Handles file uploads, drag & drop, and audio/video recording
 */

class UploadManager {
    constructor() {
        this.allowedFormats = ['mp3', 'wav', 'mp4', 'mov', 'm4a', 'ogg', 'webm'];
        this.maxFileSize = 500 * 1024 * 1024; // 500MB
        this.currentUpload = null;
        this.init();
    }

    /**
     * Initialize upload functionality
     */
    init() {
        this.setupDropZone();
        this.setupFileInput();
        this.setupRecordingButtons();
    }

    /**
     * Set up drag and drop zone
     */
    setupDropZone() {
        const dropZone = document.getElementById('drop-zone');
        
        if (!dropZone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        }, false);
    }

    /**
     * Set up file input button
     */
    setupFileInput() {
        const browseBtn = document.getElementById('browse-files-btn');
        const fileInput = document.getElementById('file-input');
        
        if (browseBtn && fileInput) {
            browseBtn.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }
    }

    /**
     * Set up recording buttons
     */
    setupRecordingButtons() {
        const recordAudioBtn = document.getElementById('record-audio-btn');
        const recordVideoBtn = document.getElementById('record-video-btn');
        
        if (recordAudioBtn) {
            recordAudioBtn.addEventListener('click', () => {
                this.startRecording('audio');
            });
        }
        
        if (recordVideoBtn) {
            recordVideoBtn.addEventListener('click', () => {
                this.startRecording('video');
            });
        }
    }

    /**
     * Prevent default drag behaviors
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Handle selected or dropped files
     */
    handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0]; // Only handle first file
        
        if (!this.validateFile(file)) {
            return;
        }
        
        this.uploadFile(file);
    }

    /**
     * Validate file format and size
     */
    validateFile(file) {
        // Check file extension
        const extension = file.name.split('.').pop().toLowerCase();
        
        if (!this.allowedFormats.includes(extension)) {
            this.showError(`File format not supported. Please use: ${this.allowedFormats.join(', ').toUpperCase()}`);
            return false;
        }
        
        // Check file size
        if (file.size > this.maxFileSize) {
            this.showError(`File is too large. Maximum size is ${this.maxFileSize / (1024 * 1024)}MB`);
            return false;
        }
        
        return true;
    }

    /**
     * Upload file with progress tracking
     */
    async uploadFile(file) {
        const progressContainer = document.getElementById('upload-progress');
        const progressBar = document.getElementById('progress-bar');
        const progressPercentage = document.getElementById('progress-percentage');
        const progressFilename = document.getElementById('progress-filename');
        
        // Show progress container
        if (progressContainer) {
            progressContainer.style.display = 'block';
            progressFilename.textContent = file.name;
        }
        
        try {
            // Show initial upload progress
            if (progressBar) {
                progressBar.style.width = '10%';
            }
            if (progressPercentage) {
                progressPercentage.textContent = '10%';
            }
            
            // Make real API call to backend
            console.log('Uploading file to backend:', file.name);
            
            const response = await window.apiClient.uploadFile(file, {
                // Use defaults from config, or could collect from user later
                meeting_type: 'consultation',
                practice_area: 'other',
                participants: 'Test User',
                notes: `Uploaded ${file.name} via frontend`
            });
            
            console.log('Upload response:', response);
            
            // Update progress to show upload complete
            if (progressBar) {
                progressBar.style.width = '100%';
            }
            if (progressPercentage) {
                progressPercentage.textContent = '100%';
            }
            
            // Show success message
            this.showSuccess(`File uploaded successfully! Job ID: ${response.job_id}`);
            
            // Redirect to processing page with job ID
            setTimeout(() => {
                window.location.href = `processing.html?job_id=${response.job_id}`;
            }, 1000);
            
        } catch (error) {
            console.error('Upload failed:', error);
            
            // Hide progress container
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
            
            // Show error message
            this.showError(error.message || 'Upload failed. Please try again.');
        }
    }

    /**
     * Start audio or video recording
     */
    async startRecording(type) {
        // Redirect to dedicated recording page
        window.location.href = 'recording.html';
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
        // Replace with a nicer notification system
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log(`Success: ${message}`);
        // Replace with a nicer notification system
    }
}

// Initialize upload manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.uploadManager = new UploadManager();
    });
} else {
    window.uploadManager = new UploadManager();
}
