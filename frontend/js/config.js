/**
 * TranscribeAI - API Configuration
 * Central configuration for backend API endpoints and settings
 */

const API_CONFIG = {
    // Backend API base URL (Docker container on port 8000)
    BASE_URL: 'http://localhost:8000/api/v1',
    
    // WebSocket URL for real-time updates
    WS_URL: 'ws://localhost:8000/ws',
    
    // Request timeout in milliseconds
    TIMEOUT: 60000, // 60 seconds
    
    // Polling interval for job status (in milliseconds)
    POLL_INTERVAL: 2000, // 2 seconds
    
    // Default values for required upload fields
    DEFAULTS: {
        meeting_type: 'consultation',  // Valid: consultation, deposition, client_update, strategy_session, etc.
        practice_area: 'other',  // Valid: family_law, corporate_law, litigation, etc., or 'other'
        participants: 'Test User',
        case_id: null,
        notes: 'Uploaded via TranscribeAI frontend'
    },
    
    // API Endpoints
    ENDPOINTS: {
        UPLOAD: '/upload',
        JOB_STATUS: (jobId) => `/upload/${jobId}/status`,
        CANCEL_JOB: (jobId) => `/upload/${jobId}`,
        TRANSCRIPTION: (jobId) => `/transcribe/${jobId}`,
        TRANSCRIBE: (jobId) => `/transcribe/${jobId}`,  // Alias for TRANSCRIPTION
        TRANSCRIBE_DOWNLOAD: (jobId, format = 'pdf') => `/transcribe/${jobId}/download?format=${format}`,
        SUMMARY: (jobId) => `/summary/${jobId}`,
        SUMMARY_REGENERATE: (jobId) => `/summary/${jobId}/regenerate`,
        SUMMARY_EXPORT: (jobId, format = 'pdf') => `/summary/${jobId}/export?format=${format}`,
        HEALTH: '/health'
    },
    
    /**
     * Get full URL for an endpoint
     */
    getFullUrl(endpoint) {
        return `${this.BASE_URL}${endpoint}`;
    }
};

/**
 * API Helper class for making requests to the backend
 */
class APIClient {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    /**
     * Make a fetch request with timeout
     */
    async fetchWithTimeout(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * Upload a file to the backend
     */
    async uploadFile(file, metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('meeting_type', metadata.meeting_type || API_CONFIG.DEFAULTS.meeting_type);
        formData.append('practice_area', metadata.practice_area || API_CONFIG.DEFAULTS.practice_area);
        formData.append('participants', metadata.participants || API_CONFIG.DEFAULTS.participants);
        
        // Only append optional fields if they have values
        if (metadata.case_id) {
            formData.append('case_id', metadata.case_id);
        }
        if (metadata.notes) {
            formData.append('notes', metadata.notes);
        }

        const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.UPLOAD}`;
        const response = await this.fetchWithTimeout(url, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            // Handle detailed error messages from backend
            let errorMessage = 'Upload failed';
            
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (error.detail.message) {
                    errorMessage = error.detail.message;
                    if (error.detail.errors && Array.isArray(error.detail.errors)) {
                        errorMessage += ': ' + error.detail.errors.join(', ');
                    }
                } else if (Array.isArray(error.detail)) {
                    // FastAPI validation errors
                    errorMessage = error.detail.map(err => `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`).join('; ');
                }
            }
            
            throw new Error(errorMessage);
        }

        return await response.json();
    }

    /**
     * Get job status
     */
    async getJobStatus(jobId) {
        const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.JOB_STATUS(jobId)}`;
        const response = await this.fetchWithTimeout(url);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get job status');
        }

        return await response.json();
    }

    /**
     * Cancel a job
     */
    async cancelJob(jobId) {
        const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.CANCEL_JOB(jobId)}`;
        const response = await this.fetchWithTimeout(url, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel job');
        }

        return await response.json();
    }

    /**
     * Get transcription results
     */
    async getTranscription(jobId) {
        const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.TRANSCRIPTION(jobId)}`;
        const response = await this.fetchWithTimeout(url);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get transcription');
        }

        return await response.json();
    }

    /**
     * Get summary results
     */
    async getSummary(jobId) {
        const url = `${this.baseURL}${API_CONFIG.ENDPOINTS.SUMMARY(jobId)}`;
        const response = await this.fetchWithTimeout(url);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get summary');
        }

        return await response.json();
    }

    /**
     * Check backend health
     */
    async checkHealth() {
        const url = `http://localhost:8000${API_CONFIG.ENDPOINTS.HEALTH}`;
        const response = await this.fetchWithTimeout(url);

        if (!response.ok) {
            throw new Error('Backend unhealthy');
        }

        return await response.json();
    }
}

// Create global API client instance
window.apiClient = new APIClient();
window.API_CONFIG = API_CONFIG;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, APIClient };
}
