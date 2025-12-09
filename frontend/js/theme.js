/**
 * TranscribeAI - Theme Management
 * Handles dark mode toggle and persistence
 */

class ThemeManager {
    constructor() {
        this.theme = this.getStoredTheme() || this.getPreferredTheme();
        this.init();
    }

    /**
     * Initialize theme on page load
     */
    init() {
        this.applyTheme(this.theme);
        this.setupToggleListener();
    }

    /**
     * Get theme from localStorage
     */
    getStoredTheme() {
        return localStorage.getItem('transcribeai-theme');
    }

    /**
     * Get user's preferred theme from system
     */
    getPreferredTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        const html = document.documentElement;
        
        if (theme === 'dark') {
            html.classList.add('dark');
            html.classList.remove('light');
        } else {
            html.classList.add('light');
            html.classList.remove('dark');
        }
        
        this.theme = theme;
        localStorage.setItem('transcribeai-theme', theme);
        this.updateToggleIcon();
    }

    /**
     * Toggle between light and dark theme
     */
    toggle() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    /**
     * Update theme toggle icon
     */
    updateToggleIcon() {
        const toggleBtn = document.getElementById('theme-toggle');
        const icon = toggleBtn?.querySelector('.material-symbols-outlined');
        
        if (icon) {
            icon.textContent = this.theme === 'light' ? 'dark_mode' : 'light_mode';
        }
    }

    /**
     * Set up event listener for theme toggle button
     */
    setupToggleListener() {
        const toggleBtn = document.getElementById('theme-toggle');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }

    /**
     * Listen for system theme changes
     */
    watchSystemTheme() {
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!this.getStoredTheme()) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}
