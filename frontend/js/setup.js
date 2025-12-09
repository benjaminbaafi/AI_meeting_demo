/**
 * TranscribeAI - Setup Manager
 * Handles initial setup/onboarding configuration
 */

class SetupManager {
    constructor() {
        this.settings = {
            language: 'en-US',
            enableTour: true,
            setupCompleted: false
        };
        this.init();
    }

    /**
     * Initialize setup manager
     */
    init() {
        this.loadSettings();
        this.setupLanguageSelector();
        this.setupTourToggle();
        this.setupButtons();
    }

    /**
     * Load existing settings
     */
    loadSettings() {
        const saved = localStorage.getItem('setup_preferences');
        if (saved) {
            try {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
            } catch (e) {
                console.error('Error loading settings:', e);
            }
        }

        // Apply loaded settings to UI
        this.applySettings();
    }

    /**
     * Apply settings to UI elements
     */
    applySettings() {
        const languageSelect = document.getElementById('language-select');
        const tourToggle = document.getElementById('tour-toggle');

        if (languageSelect) {
            languageSelect.value = this.settings.language;
        }

        if (tourToggle) {
            tourToggle.checked = this.settings.enableTour;
        }
    }

    /**
     * Set up language selector
     */
    setupLanguageSelector() {
        const languageSelect = document.getElementById('language-select');
        
        if (!languageSelect) return;

        languageSelect.addEventListener('change', (e) => {
            this.settings.language = e.target.value;
            console.log('Language changed to:', e.target.value);
        });
    }

    /**
     * Set up tour toggle
     */
    setupTourToggle() {
        const tourToggle = document.getElementById('tour-toggle');
        
        if (!tourToggle) return;

        tourToggle.addEventListener('change', (e) => {
            this.settings.enableTour = e.target.checked;
            console.log('Tour enabled:', e.target.checked);
        });
    }

    /**
     * Set up action buttons
     */
    setupButtons() {
        const finishBtn = document.getElementById('finish-btn');
        const skipBtn = document.getElementById('skip-btn');

        if (finishBtn) {
            finishBtn.addEventListener('click', () => {
                this.finishSetup();
            });
        }

        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                this.skipSetup();
            });
        }
    }

    /**
     * Complete setup with current settings
     */
    finishSetup() {
        this.settings.setupCompleted = true;
        this.saveSettings();

        // Show completion message
        this.showToast('Setup complete! Welcome to TranscribeAI', 'success');

        // Redirect based on tour preference
        setTimeout(() => {
            if (this.settings.enableTour) {
                window.location.href = 'tour.html';
            } else {
                window.location.href = 'pages/upload.html';
            }
        }, 1000);
    }

    /**
     * Skip setup and go directly to app
     */
    skipSetup() {
        // Use default settings
        this.settings.setupCompleted = true;
        this.settings.enableTour = false;
        this.saveSettings();

        this.showToast('Setup skipped - using default settings', 'info');

        // Go directly to upload page
        setTimeout(() => {
            window.location.href = 'pages/upload.html';
        }, 800);
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('setup_preferences', JSON.stringify(this.settings));
            
            // Also save to main settings for app-wide use
            const appSettings = {
                language: this.settings.language,
                darkMode: false,
                emailNotifications: true,
                pushNotifications: false
            };
            localStorage.setItem('transcribeai_settings', JSON.stringify(appSettings));
            
            console.log('Settings saved:', this.settings);
        } catch (e) {
            console.error('Error saving settings:', e);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500'
        };

        const icons = {
            success: 'check_circle',
            error: 'error',
            info: 'info'
        };

        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-slide-up`;
        toast.innerHTML = `
            <span class="material-symbols-outlined">${icons[type]}</span>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slide-up {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .animate-slide-up {
        animation: slide-up 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// Initialize setup manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.setupManager = new SetupManager();
    });
} else {
    window.setupManager = new SetupManager();
}
