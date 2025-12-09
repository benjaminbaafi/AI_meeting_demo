/**
 * TranscribeAI - Settings Manager
 * Handles user preferences, appearance, notifications, and account settings
 */

class SettingsManager {
    constructor() {
        this.settings = {
            language: 'en-US',
            darkMode: false,
            emailNotifications: true,
            pushNotifications: false
        };
        this.hasChanges = false;
        this.init();
    }

    /**
     * Initialize settings manager
     */
    init() {
        this.loadSettings();
        this.setupLanguageSelect();
        this.setupDarkModeToggle();
        this.setupNotificationToggles();
        this.setupActionButtons();
    }

    /**
     * Load settings from localStorage
     */
    loadSettings() {
        const saved = localStorage.getItem('transcribeai_settings');
        if (saved) {
            try {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
                console.log('Settings loaded:', this.settings);
            } catch (e) {
                console.error('Error loading settings:', e);
            }
        }
        this.applySettings();
    }

    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('transcribeai_settings', JSON.stringify(this.settings));
            console.log('Settings saved:', this.settings);
            this.hasChanges = false;
            this.updateSaveButton();
            this.showSuccessMessage();
        } catch (e) {
            console.error('Error saving settings:', e);
            this.showErrorMessage();
        }
    }

    /**
     * Apply settings to UI
     */
    applySettings() {
        // Apply language
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.value = this.settings.language;
        }

        // Dark mode is handled by theme.js
        // But we sync the toggle state
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        if (darkModeToggle) {
            const isDark = document.documentElement.classList.contains('dark');
            this.updateToggleState(darkModeToggle, isDark);
        }

        // Apply notification settings
        const emailToggle = document.getElementById('email-notifications-toggle');
        if (emailToggle) {
            this.updateToggleState(emailToggle, this.settings.emailNotifications);
        }

        const pushToggle = document.getElementById('push-notifications-toggle');
        if (pushToggle) {
            this.updateToggleState(pushToggle, this.settings.pushNotifications);
        }
    }

    /**
     * Set up language selector
     */
    setupLanguageSelect() {
        const languageSelect = document.getElementById('language-select');
        
        if (!languageSelect) return;

        languageSelect.addEventListener('change', (e) => {
            this.settings.language = e.target.value;
            this.hasChanges = true;
            this.updateSaveButton();
            console.log('Language changed to:', e.target.value);
        });
    }

    /**
     * Set up dark mode toggle
     */
    setupDarkModeToggle() {
        const toggle = document.getElementById('dark-mode-toggle');
        
        if (!toggle) return;

        toggle.addEventListener('click', () => {
            // Use theme manager to toggle
            if (window.themeManager) {
                window.themeManager.toggle();
            }
            
            // Update toggle state
            const isDark = document.documentElement.classList.contains('dark');
            this.updateToggleState(toggle, isDark);
            this.settings.darkMode = isDark;
            
            // Don't mark as changed since theme manager handles persistence
        });
    }

    /**
     * Set up notification toggles
     */
    setupNotificationToggles() {
        const emailToggle = document.getElementById('email-notifications-toggle');
        const pushToggle = document.getElementById('push-notifications-toggle');

        if (emailToggle) {
            emailToggle.addEventListener('click', () => {
                this.settings.emailNotifications = !this.settings.emailNotifications;
                this.updateToggleState(emailToggle, this.settings.emailNotifications);
                this.hasChanges = true;
                this.updateSaveButton();
            });
        }

        if (pushToggle) {
            pushToggle.addEventListener('click', () => {
                this.settings.pushNotifications = !this.settings.pushNotifications;
                this.updateToggleState(pushToggle, this.settings.pushNotifications);
                this.hasChanges = true;
                this.updateSaveButton();
            });
        }
    }

    /**
     * Update toggle button state
     */
    updateToggleState(toggle, isActive) {
        const slider = toggle.querySelector('span[aria-hidden="true"]');
        
        toggle.setAttribute('aria-checked', isActive.toString());
        
        if (isActive) {
            toggle.classList.remove('bg-gray-200', 'dark:bg-gray-700');
            toggle.classList.add('bg-primary');
            if (slider) {
                slider.classList.remove('translate-x-0');
                slider.classList.add('translate-x-5');
            }
        } else {
            toggle.classList.add('bg-gray-200', 'dark:bg-gray-700');
            toggle.classList.remove('bg-primary');
            if (slider) {
                slider.classList.add('translate-x-0');
                slider.classList.remove('translate-x-5');
            }
        }
    }

    /**
     * Set up action buttons
     */
    setupActionButtons() {
        const saveBtn = document.getElementById('save-btn');
        const cancelBtn = document.getElementById('cancel-btn');

        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveSettings();
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelChanges();
            });
        }

        // Update save button initial state
        this.updateSaveButton();
    }

    /**
     * Update save button state
     */
    updateSaveButton() {
        const saveBtn = document.getElementById('save-btn');
        
        if (!saveBtn) return;

        if (this.hasChanges) {
            saveBtn.disabled = false;
            saveBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            saveBtn.disabled = true;
            saveBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    /**
     * Cancel changes and reload settings
     */
    cancelChanges() {
        if (this.hasChanges) {
            if (confirm('Are you sure you want to discard your changes?')) {
                this.loadSettings();
                this.hasChanges = false;
                this.updateSaveButton();
                console.log('Changes cancelled');
            }
        }
    }

    /**
     * Show success message
     */
    showSuccessMessage() {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-slide-up';
        toast.innerHTML = `
            <span class="material-symbols-outlined">check_circle</span>
            <span>Settings saved successfully</span>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    /**
     * Show error message
     */
    showErrorMessage() {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-slide-up';
        toast.innerHTML = `
            <span class="material-symbols-outlined">error</span>
            <span>Error saving settings</span>
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

// Initialize settings manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.settingsManager = new SettingsManager();
    });
} else {
    window.settingsManager = new SettingsManager();
}
