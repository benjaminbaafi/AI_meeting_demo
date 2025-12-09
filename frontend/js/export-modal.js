/**
 * TranscribeAI - Export Modal Manager
 * Handles export report modal interactions and file generation
 */

class ExportModalManager {
    constructor() {
        this.selectedFormat = 'pdf';
        this.selectedRange = '7';
        this.startDate = null;
        this.endDate = null;
        this.init();
    }

    /**
     * Initialize export modal
     */
    init() {
        this.setupFormatSelection();
        this.setupDatePresets();
        this.setupDateInputs();
        this.setupActions();
        this.loadDefaults();
    }

    /**
     * Load default values
     */
    loadDefaults() {
        // Set default dates
        const today = new Date();
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(today.getDate() - 7);

        this.startDate = sevenDaysAgo;
        this.endDate = today;

        // Update inputs
        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');

        if (startInput && endInput) {
            startInput.value = this.formatDateForInput(this.startDate);
            endInput.value = this.formatDateForInput(this.endDate);
        }
    }

    /**
     * Format date for input field (YYYY-MM-DD)
     */
    formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    /**
     * Set up file format selection
     */
    setupFormatSelection() {
        const radioButtons = document.querySelectorAll('input[name="file-format"]');
        
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectedFormat = e.target.value;
                console.log('Format selected:', this.selectedFormat);
            });
        });
    }

    /**
     * Set up date range presets
     */
    setupDatePresets() {
        const presetBtns = document.querySelectorAll('.preset-btn');
        
        presetBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const range = btn.getAttribute('data-range');
                this.selectPreset(range);
                this.updatePresetButtons(range);
            });
        });
    }

    /**
     * Select date range preset
     */
    selectPreset(range) {
        this.selectedRange = range;
        const today = new Date();
        let startDate = new Date(today);

        switch(range) {
            case '7':
                startDate.setDate(today.getDate() - 7);
                break;
            case '30':
                startDate.setDate(today.getDate() - 30);
                break;
            case 'month':
                startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                break;
        }

        this.startDate = startDate;
        this.endDate = today;

        // Update inputs
        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');

        if (startInput && endInput) {
            startInput.value = this.formatDateForInput(startDate);
            endInput.value = this.formatDateForInput(today);
        }

        console.log('Preset selected:', range);
    }

    /**
     * Update preset button states
     */
    updatePresetButtons(activeRange) {
        document.querySelectorAll('.preset-btn').forEach(btn => {
            const btnRange = btn.getAttribute('data-range');
            if (btnRange === activeRange) {
                btn.classList.remove('bg-gray-200', 'dark:bg-gray-800', 'text-slate-800', 'dark:text-white');
                btn.classList.add('bg-primary/20', 'text-primary');
            } else {
                btn.classList.add('bg-gray-200', 'dark:bg-gray-800', 'text-slate-800', 'dark:text-white');
                btn.classList.remove('bg-primary/20', 'text-primary');
            }
        });
    }

    /**
     * Set up date inputs
     */
    setupDateInputs() {
        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');

        if (startInput) {
            startInput.addEventListener('change', (e) => {
                this.startDate = new Date(e.target.value);
                console.log('Start date:', this.startDate);
            });
        }

        if (endInput) {
            endInput.addEventListener('change', (e) => {
                this.endDate = new Date(e.target.value);
                console.log('End date:', this.endDate);
            });
        }
    }

    /**
     * Set up action buttons
     */
    setupActions() {
        const exportBtn = document.getElementById('export-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        const closeBtn = document.getElementById('close-modal');

        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    /**
     * Export report
     */
    exportReport() {
        console.log('Exporting report:', {
            format: this.selectedFormat,
            startDate: this.startDate,
            endDate: this.endDate
        });

        if (this.selectedFormat === 'pdf') {
            this.exportPDF();
        } else if (this.selectedFormat === 'csv') {
            this.exportCSV();
        }
    }

    /**
     * Export as PDF
     */
    exportPDF() {
        this.showToast('Generating PDF report...', 'info');
        
        // Simulate PDF generation
        setTimeout(() => {
            this.showToast('PDF export feature coming soon!', 'info');
            console.log('PDF would be downloaded here');
        }, 1000);
    }

    /**
     * Export as CSV
     */
    exportCSV() {
        // Generate CSV data with date range
        const csvData = this.generateCSVData();
        
        // Create blob and download
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const dateStr = `${this.formatDateForFilename(this.startDate)}_to_${this.formatDateForFilename(this.endDate)}`;
        a.download = `transcribeai-report-${dateStr}.csv`;
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('CSV report downloaded successfully', 'success');
        
        // Close modal after short delay
        setTimeout(() => {
            this.closeModal();
        }, 1500);
    }

    /**
     * Format date for filename
     */
    formatDateForFilename(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}${month}${day}`;
    }

    /**
     * Generate CSV data
     */
    generateCSVData() {
        const headers = ['Metric', 'Value', 'Change', 'Date Range'];
        const dateRange = `${this.startDate.toLocaleDateString()} - ${this.endDate.toLocaleDateString()}`;
        
        const rows = [
            ['Report Generated', new Date().toLocaleString(), '', ''],
            ['Date Range', dateRange, '', ''],
            ['', '', '', ''],
            ['Total Transcription Minutes', '1,234', '+12.5%', dateRange],
            ['Files Processed', '86', '+8.1%', dateRange],
            ['Total Cost', '$152.50', '+21.3%', dateRange],
            ['Average Accuracy', '97.8%', '-0.2%', dateRange],
            ['', '', '', ''],
            ['Language Accuracy', '', '', ''],
            ['English (US)', '98.5%', '', dateRange],
            ['Spanish', '96.2%', '', dateRange],
            ['French', '95.8%', '', dateRange],
            ['German', '94.1%', '', dateRange]
        ];

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Close modal
     */
    closeModal() {
        // Redirect back to analytics page or close window
        if (document.referrer.includes('analytics')) {
            window.history.back();
        } else {
            window.location.href = 'analytics.html';
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

// Initialize export modal manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.exportModalManager = new ExportModalManager();
    });
} else {
    window.exportModalManager = new ExportModalManager();
}
