/**
 * Upload Manager
 * Handles file uploads and processing with backend API
 */

class UploadManager {
    constructor() {
        this.currentJobId = null;
        this.currentFile = null;
        this.websocket = null;
        this.progressCallback = null;
        this.resultsCallback = null;
        this.errorCallback = null;
    }

    /**
     * Upload a file to the backend
     */
    async uploadFile(file, metadata) {
        try {
            console.log('Uploading file:', file.name);
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('meeting_type', metadata.meeting_type || 'consultation');
            formData.append('practice_area', metadata.practice_area || 'employment_law');
            formData.append('participants', metadata.participants || '');
            
            if (metadata.case_id) {
                formData.append('case_id', metadata.case_id);
            }

            const response = await fetch(
                window.API_CONFIG.getFullUrl(window.API_CONFIG.ENDPOINTS.UPLOAD),
                {
                    method: 'POST',
                    body: formData
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const data = await response.json();
            this.currentJobId = data.job_id;
            this.currentFile = file;

            console.log('✅ Upload successful, Job ID:', this.currentJobId);

            // Connect WebSocket for real-time updates
            this.connectWebSocket(this.currentJobId);

            return data;

        } catch (error) {
            console.error('Upload error:', error);
            if (this.errorCallback) {
                this.errorCallback(error);
            }
            throw error;
        }
    }

    /**
     * Connect WebSocket for real-time updates
     */
    connectWebSocket(jobId) {
        const wsUrl = window.API_CONFIG.getWsUrl(
            window.API_CONFIG.ENDPOINTS.WS_JOB(jobId)
        );

        console.log('Connecting to WebSocket:', wsUrl);

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('✅ WebSocket connected');
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message:', data);

            // Update progress
            if (this.progressCallback) {
                this.progressCallback({
                    progress: data.progress || 0,
                    step: data.current_step || 'Processing...',
                    status: data.status
                });
            }

            // Fetch results when completed
            if (data.status === 'completed') {
                setTimeout(() => {
                    this.fetchResults(jobId);
                }, 1000);
            } else if (data.status === 'failed') {
                if (this.errorCallback) {
                    this.errorCallback(new Error(data.message || 'Processing failed'));
                }
            }
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
        };

        // Keep-alive ping
        this.pingInterval = setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send('ping');
            }
        }, 30000);
    }

    /**
     * Fetch job status
     */
    async getJobStatus(jobId) {
        const response = await fetch(
            window.API_CONFIG.getFullUrl(
                window.API_CONFIG.ENDPOINTS.UPLOAD_STATUS(jobId)
            )
        );

        if (!response.ok) {
            throw new Error('Failed to fetch job status');
        }

        return await response.json();
    }

    /**
     * Fetch transcription and summary results
     */
    async fetchResults(jobId) {
        try {
            console.log('Fetching results for job:', jobId);

            // Fetch transcription
            const transcriptResponse = await fetch(
                window.API_CONFIG.getFullUrl(
                    window.API_CONFIG.ENDPOINTS.TRANSCRIBE(jobId)
                )
            );

            if (!transcriptResponse.ok) {
                throw new Error('Failed to fetch transcription');
            }

            const transcription = await transcriptResponse.json();

            // Fetch summary
            const summaryResponse = await fetch(
                window.API_CONFIG.getFullUrl(
                    window.API_CONFIG.ENDPOINTS.SUMMARY(jobId)
                )
            );

            if (!summaryResponse.ok) {
                throw new Error('Failed to fetch summary');
            }

            const summary = await summaryResponse.json();

            console.log('✅ Results fetched successfully');

            // Call results callback
            if (this.resultsCallback) {
                this.resultsCallback({
                    transcription,
                    summary,
                    jobId
                });
            }

            return { transcription, summary };

        } catch (error) {
            console.error('Error fetching results:', error);
            if (this.errorCallback) {
                this.errorCallback(error);
            }
            throw error;
        }
    }

    /**
     * Export transcription
     */
    exportTranscription(jobId, format = 'pdf') {
        const url = window.API_CONFIG.getFullUrl(
            window.API_CONFIG.ENDPOINTS.TRANSCRIBE_DOWNLOAD(jobId, format)
        );
        window.open(url, '_blank');
    }

    /**
     * Export summary
     */
    exportSummary(jobId, format = 'pdf') {
        const url = window.API_CONFIG.getFullUrl(
            window.API_CONFIG.ENDPOINTS.SUMMARY_EXPORT(jobId, format)
        );
        window.open(url, '_blank');
    }

    /**
     * Regenerate summary with different type
     */
    async regenerateSummary(jobId, summaryType) {
        const response = await fetch(
            window.API_CONFIG.getFullUrl(
                window.API_CONFIG.ENDPOINTS.SUMMARY_REGENERATE(jobId)
            ) + `?summary_type=${summaryType}`,
            {
                method: 'POST'
            }
        );

        if (!response.ok) {
            throw new Error('Failed to regenerate summary');
        }

        return await response.json();
    }

    /**
     * Set progress callback
     */
    onProgress(callback) {
        this.progressCallback = callback;
    }

    /**
     * Set results callback
     */
    onResults(callback) {
        this.resultsCallback = callback;
    }

    /**
     * Set error callback
     */
    onError(callback) {
        this.errorCallback = callback;
    }

    /**
     * Cleanup
     */
    cleanup() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }

        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }

        this.currentJobId = null;
        this.currentFile = null;
    }
}

// Export to window
window.UploadManager = UploadManager;
