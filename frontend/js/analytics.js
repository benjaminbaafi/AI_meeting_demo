/**
 * TranscribeAI - Analytics Manager
 * Handles analytics dashboard interactions, filters, and export functionality
 */

class AnalyticsManager {
    constructor() {
        this.selectedFormat = 'csv';
        this.selectedRange = '30';
        this.init();
    }

    /**
     * Initialize analytics manager
     */
    init() {
        this.setupFormatSelector();
        this.setupRangeSelector();
        this.setupExport();
    }

    /**
     * Set up report format selector
     */
    setupFormatSelector() {
        const formatBtns = document.querySelectorAll('.format-btn');
        
        formatBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const format = btn.getAttribute('data-format');
                this.selectFormat(format);
            });
        });
    }

    /**
     * Select report format
     */
    selectFormat(format) {
        this.selectedFormat = format;

        // Update button states
        document.querySelectorAll('.format-btn').forEach(btn => {
            const btnFormat = btn.getAttribute('data-format');
            if (btnFormat === format) {
                btn.classList.add('bg-gray-100', 'dark:bg-background-dark', 'text-slate-800', 'dark:text-white');
                btn.classList.remove('text-slate-600', 'dark:text-gray-400');
            } else {
                btn.classList.remove('bg-gray-100', 'dark:bg-background-dark', 'text-slate-800', 'dark:text-white');
                btn.classList.add('text-slate-600', 'dark:text-gray-400');
            }
        });

        console.log('Format selected:', format);
    }

    /**
     * Set up date range selector
     */
    setupRangeSelector() {
        const rangeBtns = document.querySelectorAll('.range-btn');
        
        rangeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const range = btn.getAttribute('data-range');
                if (range === 'custom') {
                    this.showCustomDatePicker();
                } else {
                    this.selectRange(range);
                }
            });
        });
    }

    /**
     * Select date range
     */
    selectRange(range) {
        this.selectedRange = range;

        // Update button states
        document.querySelectorAll('.range-btn').forEach(btn => {
            const btnRange = btn.getAttribute('data-range');
            if (btnRange === range) {
                btn.classList.add('bg-gray-100', 'dark:bg-background-dark', 'text-slate-800', 'dark:text-white');
                btn.classList.remove('text-slate-600', 'dark:text-gray-400');
            } else {
                btn.classList.remove('bg-gray-100', 'dark:bg-background-dark', 'text-slate-800', 'dark:text-white');
                btn.classList.add('text-slate-600', 'dark:text-gray-400');
            }
        });

        console.log('Range selected:', range);
        // In production, this would fetch new data
    }

    /**
     * Show custom date picker dialog
     */
    showCustomDatePicker() {
        // In production, implement custom date range picker
        alert('Custom date picker would appear here. In production, this would show a calendar UI to select start and end dates.');
    }

    /**
     * Set up export functionality
     */
    setupExport() {
        const exportBtn = document.getElementById('export-btn');
        
        if (!exportBtn) return;

        exportBtn.addEventListener('click', () => {
            this.exportReport();
        });
    }

    /**
     * Export report
     */
    exportReport() {
        const format = this.selectedFormat;
        const range = this.selectedRange;

        console.log(`Exporting ${format} report for range: ${range}`);

        if (format === 'csv') {
            this.exportCSV();
        } else if (format === 'pdf') {
            this.exportPDF();
        }
    }

    /**
     * Export as CSV
     */
    exportCSV() {
        // Generate CSV data
        const csvData = this.generateCSVData();
        
        // Create blob and download
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcribeai-analytics-${this.selectedRange}days-${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('CSV report downloaded successfully', 'success');
    }

    /**
     * Generate CSV data
     */
    generateCSVData() {
        // In production, this would use actual data
        const headers = ['Metric', 'Value', 'Change'];
        const rows = [
            ['Total Transcription Minutes', '1,234', '+12.5%'],
            ['Files Processed', '86', '+8.1%'],
            ['Total Cost', '$152.50', '+21.3%'],
            ['Average Accuracy', '97.8%', '-0.2%'],
            ['', '', ''],
            ['Language Accuracy', '', ''],
            ['English (US)', '98.5%', ''],
            ['Spanish', '96.2%', ''],
            ['French', '95.8%', ''],
            ['German', '94.1%', ''],
            ['', '', ''],
            ['Processing Time', '', ''],
            ['Average', '45s', ''],
            ['Minimum', '12s', ''],
            ['Maximum', '2m 15s', '']
        ];

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    /**
     * Export as PDF
     */
    exportPDF() {
        // In production, generate actual PDF
        this.showToast('Generating PDF report...', 'info');
        
        setTimeout(() => {
            this.showToast('PDF export feature coming soon!', 'info');
            console.log('PDF export would download here');
        }, 1000);
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

// Initialize analytics manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.analyticsManager = new AnalyticsManager();
    });
} else {
    window.analyticsManager = new AnalyticsManager();
}
