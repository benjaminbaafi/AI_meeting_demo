/**
 * TranscribeAI - Processing Page
 * Polls backend for job status and updates UI with real-time progress
 */

class ProcessingManager {
    constructor() {
        this.jobId = null;
        this.pollInterval = null;
        this.statusMapping = {
            'queued': { step: 0, text: 'Initializing...' },
            'processing': { step: 2, text: 'Transcribing audio...' },
            'completed': { step: 4, text: 'Completed!' },
            'failed': { step: 0, text: 'Processing failed' },
            'cancelled': { step: 0, text: 'Cancelled' }
        };
        this.init();
    }

    /**
     * Initialize processing page
     */
    init() {
        // Get job ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        this.jobId = urlParams.get('job_id');

        if (!this.jobId) {
            console.error('No job ID provided');
            this.showError('No job ID found. Redirecting to upload page...');
            setTimeout(() => {
                window.location.href = 'upload.html';
            }, 2000);
            return;
        }

        console.log('Processing job:', this.jobId);

        // Setup cancel button
        this.setupCancelButton();

        // Start polling for status
        this.startPolling();
    }

    /**
     * Setup cancel button click handler
     */
    setupCancelButton() {
        const cancelBtn = document.getElementById('cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', async () => {
                if (confirm('Are you sure you want to cancel this processing?')) {
                    await this.cancelJob();
                }
            });
        }
    }

    /**
     * Start polling backend for job status
     */
    startPolling() {
        // Poll immediately
        this.pollStatus();

        // Then poll every 2 seconds
        this.pollInterval = setInterval(() => {
            this.pollStatus();
        }, 2000);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * Poll for job status
     */
    async pollStatus() {
        try {
            const status = await window.apiClient.getJobStatus(this.jobId);
            console.log('Job status:', status);

            // Update UI with status
            this.updateUI(status);

            // Handle completion
            if (status.status === 'completed') {
                this.stopPolling();
                this.onComplete();
            } else if (status.status === 'failed') {
                this.stopPolling();
                this.onFailed(status.error || 'Processing failed');
            } else if (status.status === 'cancelled') {
                this.stopPolling();
                this.onCancelled();
            }

        } catch (error) {
            console.error('Failed to get job status:', error);
            // Don't stop polling on error, just log it
            // Backend might be temporarily unavailable
        }
    }

    /**
     * Update UI based on job status
     */
    updateUI(status) {
        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.querySelector('.progress-title');
        const progressPercentage = document.querySelector('.text-primary.text-sm');

        if (progressBar) {
            progressBar.style.width = `${status.progress_percentage}%`;
        }

        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(status.progress_percentage)}%`;
        }

        if (progressText) {
            progressText.textContent = status.current_step || 'Processing...';
        }

        // Update page title
        const pageTitle = document.querySelector('h1');
        if (pageTitle && status.status === 'processing') {
            pageTitle.textContent = status.current_step || 'Analyzing your file...';
        }

        // Update step checkboxes based on progress
        this.updateSteps(status);
    }

    /**
     * Update processing step checkboxes
     */
    updateSteps(status) {
        const steps = [
            { selector: 'input[type="checkbox"]:nth-of-type(1)', threshold: 10 },  // Upload
            { selector: 'input[type="checkbox"]:nth-of-type(2)', threshold: 30 },  // Transcribe
            { selector: 'input[type="checkbox"]:nth-of-type(3)', threshold: 70 },  // Analyze
            { selector: 'input[type="checkbox"]:nth-of-type(4)', threshold: 100 }  // Summary
        ];

        steps.forEach(step => {
            const checkbox = document.querySelector(step.selector);
            if (checkbox) {
                checkbox.checked = status.progress_percentage >= step.threshold;
                
                // Update parent label styling
                const label = checkbox.closest('label');
                if (label) {
                    if (status.progress_percentage >= step.threshold) {
                        label.classList.remove('opacity-60');
                    } else if (status.progress_percentage >= step.threshold - 10) {
                        // Currently processing this step
                        label.classList.remove('opacity-60');
                        const text = label.querySelector('p');
                        if (text) {
                            text.classList.add('text-primary', 'font-medium');
                        }
                    }
                }
            }
        });
    }

    /**
     * Handle job completion
     */
    onComplete() {
        console.log('Job completed successfully!');
        
        // Update UI to show completion
        const pageTitle = document.querySelector('h1');
        if (pageTitle) {
            pageTitle.textContent = '✓ Processing Complete!';
        }

        const progressText = document.querySelector('.progress-title');
        if (progressText) {
            progressText.textContent = 'Done! Redirecting to results...';
        }

        // Redirect to results page
        setTimeout(() => {
            window.location.href = `results.html?job=${this.jobId}`;
        }, 2000);
    }

    /**
     * Handle job failure
     */
    onFailed(errorMessage) {
        console.error('Job failed:', errorMessage);
        
        const pageTitle = document.querySelector('h1');
        if (pageTitle) {
            pageTitle.textContent = 'Processing Failed';
        }

        const progressText = document.querySelector('.progress-title');
        if (progressText) {
            progressText.textContent = errorMessage || 'An error occurred during processing';
            progressText.classList.add('text-red-500');
        }

        // Show error message
        this.showError(errorMessage || 'Processing failed. Please try again.');
    }

    /**
     * Handle job cancellation
     */
    onCancelled() {
        console.log('Job cancelled');
        window.location.href = 'upload.html';
    }

    /**
     * Cancel the current job
     */
    async cancelJob() {
        try {
            await window.apiClient.cancelJob(this.jobId);
            this.stopPolling();
            this.onCancelled();
        } catch (error) {
            console.error('Failed to cancel job:', error);
            this.showError('Failed to cancel job. Please try again.');
        }
    }

    /**
     * Show error message (placeholder)
     */
    showError(message) {
        console.error('Error:', message);
        alert(`Error: ${message}`);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.processingManager = new ProcessingManager();
    });
} else {
    window.processingManager = new ProcessingManager();
}
