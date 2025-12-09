/**
 * TranscribeAI - Main Application JavaScript
 * Core functionality and utilities
 */

// Application configuration
const APP_CONFIG = {
    name: 'TranscribeAI',
    version: '1.0.0',
    apiEndpoint: '/api', // Placeholder for backend API
};

/**
 * Main application class
 */
class TranscribeAI {
    constructor() {
        this.init();
    }

    /**
     * Initialize application
     */
    init() {
        console.log(`${APP_CONFIG.name} v${APP_CONFIG.version} initialized`);
        this.setupEventListeners();
        this.setupNavigation();
    }

    /**
     * Set up global event listeners
     */
    setupEventListeners() {
        // Add any global event listeners here
        window.addEventListener('error', this.handleError.bind(this));
    }

    /**
     * Set up navigation
     */
    setupNavigation() {
        // Highlight current page in navigation
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (currentPath.includes(href) && href !== '#') {
                link.classList.add('active');
            }
        });
    }

    /**
     * Global error handler
     */
    handleError(event) {
        console.error('Application error:', event.error);
        // Implement error reporting or user notification here
    }

    /**
     * Utility: Format file size
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Utility: Format duration
     */
    static formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Utility: Debounce function
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new TranscribeAI();
    });
} else {
    window.app = new TranscribeAI();
}
