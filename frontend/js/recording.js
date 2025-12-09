/**
 * TranscribeAI - Recording Interface Manager
 * Handles media recording (video, audio, screen) with preview and controls
 */

class RecordingManager {
    constructor() {
        this.mediaStream = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.recordingType = 'video'; // 'video', 'audio', 'screen'
        this.isRecording = false;
        this.isPaused = false;
        this.startTime = null;
        this.elapsedTime = 0;
        this.timerInterval = null;
        
        this.init();
    }

    /**
     * Initialize recording manager
     */
    init() {
        this.setupTypeSelector();
        this.setupControls();
        this.setupPermissionsButton();
    }

    /**
     * Set up recording type selector
     */
    setupTypeSelector() {
        const typeInputs = document.querySelectorAll('input[name="recording-type"]');
        
        typeInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.recordingType = e.target.value;
                console.log('Recording type changed to:', this.recordingType);
                
                // Stop current stream if switching types
                if (this.mediaStream) {
                    this.stopMediaStream();
                }
            });
        });
    }

    /**
     * Set up recording controls
     */
    setupControls() {
        const recordBtn = document.getElementById('record-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        
        if (recordBtn) {
            recordBtn.addEventListener('click', () => {
                if (!this.isRecording) {
                    this.startRecording();
                } else {
                    this.stopRecording();
                }
            });
        }
        
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (this.isPaused) {
                    this.resumeRecording();
                } else {
                    this.pauseRecording();
                }
            });
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelRecording();
            });
        }
    }

    /**
     * Set up permissions request button
     */
    setupPermissionsButton() {
        const permBtn = document.getElementById('request-permissions-btn');
        
        if (permBtn) {
            permBtn.addEventListener('click', async () => {
                await this.requestMediaPermissions();
            });
        }
    }

    /**
     * Request media permissions and start preview
     */
    async requestMediaPermissions() {
        try {
            const constraints = this.getMediaConstraints();
            
            if (this.recordingType === 'screen') {
                this.mediaStream = await navigator.mediaDevices.getDisplayMedia(constraints);
            } else {
                this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            }
            
            this.showPreview();
            this.hidePermissionsMessage();
            
        } catch (error) {
            console.error('Error accessing media devices:', error);
            this.showError('Could not access camera/microphone. Please check your permissions.');
        }
    }

    /**
     * Get media constraints based on recording type
     */
    getMediaConstraints() {
        switch (this.recordingType) {
            case 'video':
                return { video: true, audio: true };
            case 'audio':
                return { audio: true };
            case 'screen':
                return { video: { mediaSource: 'screen' }, audio: true };
            default:
                return { video: true, audio: true };
        }
    }

    /**
     * Show video preview
     */
    showPreview() {
        const videoElement = document.getElementById('video-preview');
        
        if (this.recordingType !== 'audio' && videoElement) {
            videoElement.srcObject = this.mediaStream;
            videoElement.classList.add('active');
        }
    }

    /**
     * Hide permissions message
     */
    hidePermissionsMessage() {
        const cameraOffState = document.getElementById('camera-off-state');
        if (cameraOffState) {
            cameraOffState.style.display = 'none';
        }
    }

    /**
     * Start recording
     */
    async startRecording() {
        // Request permissions if not already granted
        if (!this.mediaStream) {
            await this.requestMediaPermissions();
            if (!this.mediaStream) return;
        }

        try {
            this.recordedChunks = [];
            
            // Create media recorder
            const options = { mimeType: 'video/webm;codecs=vp9' };
            this.mediaRecorder = new MediaRecorder(this.mediaStream, options);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.onRecordingComplete();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.startTimer();
            this.updateUI('recording');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showError('Could not start recording. Please try again.');
        }
    }

    /**
     * Stop recording
     */
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.stopTimer();
            this.updateUI('stopped');
        }
    }

    /**
     * Pause recording
     */
    pauseRecording() {
        if (this.mediaRecorder && this.isRecording && !this.isPaused) {
            this.mediaRecorder.pause();
            this.isPaused = true;
            this.stopTimer();
            this.updateUI('paused');
        }
    }

    /**
     * Resume recording
     */
    resumeRecording() {
        if (this.mediaRecorder && this.isRecording && this.isPaused) {
            this.mediaRecorder.resume();
            this.isPaused = false;
            this.startTimer();
            this.updateUI('recording');
        }
    }

    /**
     * Cancel recording
     */
    cancelRecording() {
        const confirmed = confirm('Are you sure you want to cancel this recording?');
        
        if (confirmed) {
            if (this.mediaRecorder && this.isRecording) {
                this.mediaRecorder.stop();
            }
            
            this.isRecording = false;
            this.isPaused = false;
            this.recordedChunks = [];
            this.stopTimer();
            this.resetTimer();
            this.stopMediaStream();
            this.updateUI('idle');
            
            // Redirect back to upload page
            window.location.href = 'upload.html';
        }
    }

    /**
     * Handle recording completion
     */
    onRecordingComplete() {
        const blob = new Blob(this.recordedChunks, {
            type: this.recordingType === 'audio' ? 'audio/webm' : 'video/webm'
        });
        
        console.log('Recording complete. Size:', TranscribeAI.formatFileSize(blob.size));
        
        // Create a file from the blob
        const file = new File([blob], `recording-${Date.now()}.webm`, {
            type: blob.type
        });
        
        // Simulate upload (in real app, upload to server)
        this.uploadRecording(file);
    }

    /**
     * Upload recording
     */
    uploadRecording(file) {
        console.log('Uploading recording:', file.name);
        
        // Show success message
        alert('Recording saved! Redirecting to processing...');
        
        // Redirect to processing page
        setTimeout(() => {
            window.location.href = 'processing.html';
        }, 1000);
    }

    /**
     * Start timer
     */
    startTimer() {
        this.startTime = Date.now() - this.elapsedTime;
        
        this.timerInterval = setInterval(() => {
            this.elapsedTime = Date.now() - this.startTime;
            this.updateTimerDisplay();
        }, 100);
        
        // Show recording indicator
        const recIndicator = document.getElementById('rec-indicator');
        if (recIndicator) {
            recIndicator.style.display = 'flex';
        }
    }

    /**
     * Stop timer
     */
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    /**
     * Reset timer
     */
    resetTimer() {
        this.elapsedTime = 0;
        this.updateTimerDisplay();
        
        // Hide recording indicator
        const recIndicator = document.getElementById('rec-indicator');
        if (recIndicator) {
            recIndicator.style.display = 'none';
        }
    }

    /**
     * Update timer display
     */
    updateTimerDisplay() {
        const seconds = Math.floor(this.elapsedTime / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        
        const mainTimer = document.getElementById('main-timer');
        const recTimeDisplay = document.getElementById('rec-time-display');
        
        if (mainTimer) mainTimer.textContent = timeString;
        if (recTimeDisplay) recTimeDisplay.textContent = timeString;
    }

    /**
     * Update UI based on state
     */
    updateUI(state) {
        const recordBtn = document.getElementById('record-btn');
        const pauseBtn = document.getElementById('pause-btn');
        const recordIcon = recordBtn?.querySelector('.material-symbols-outlined');
        const pauseIcon = pauseBtn?.querySelector('.material-symbols-outlined');
        
        switch (state) {
            case 'recording':
                if (recordIcon) recordIcon.textContent = 'stop';
                if (recordBtn) recordBtn.title = 'Stop Recording';
                if (pauseBtn) pauseBtn.style.display = 'flex';
                if (pauseIcon) pauseIcon.textContent = 'pause';
                break;
                
            case 'paused':
                if (pauseIcon) pauseIcon.textContent = 'play_arrow';
                break;
                
            case 'stopped':
            case 'idle':
                if (recordIcon) recordIcon.textContent = 'fiber_manual_record';
                if (recordBtn) recordBtn.title = 'Start Recording';
                if (pauseBtn) pauseBtn.style.display = 'none';
                if (pauseIcon) pauseIcon.textContent = 'pause';
                break;
        }
    }

    /**
     * Stop media stream
     */
    stopMediaStream() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
            
            const videoElement = document.getElementById('video-preview');
            if (videoElement) {
                videoElement.srcObject = null;
                videoElement.classList.remove('active');
            }
            
            // Show permissions message again
            const cameraOffState = document.getElementById('camera-off-state');
            if (cameraOffState) {
                cameraOffState.style.display = 'flex';
            }
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(`Error: ${message}`);
        // Replace with better UI notification
    }
}

// Initialize recording manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.recordingManager = new RecordingManager();
    });
} else {
    window.recordingManager = new RecordingManager();
}
