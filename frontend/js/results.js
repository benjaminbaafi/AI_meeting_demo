/**
 * Results Page - Display Transcription and Summary
 * Fetches job results from backend API
 */

class ResultsManager {
    constructor() {
        this.jobId = null;
        this.transcription = null;
        this.summary = null;
        this.init();
    }

    init() {
        // Get job ID from URL or session storage
        const urlParams = new URLSearchParams(window.location.search);
        this.jobId = urlParams.get('job') || sessionStorage.getItem('currentJobId');

        if (!this.jobId) {
            console.error('No job ID found');
            alert('No job ID found. Redirecting to upload page.');
            window.location.href = 'upload.html';
            return;
        }

        // Load results
        this.loadResults();

        // Setup event listeners
        this.setupEventListeners();
    }

    async loadResults() {
        try {
            console.log('Loading results for job:', this.jobId);

            // Fetch transcription
            const transResponse = await fetch(
                window.API_CONFIG.getFullUrl(
                    window.API_CONFIG.ENDPOINTS.TRANSCRIBE(this.jobId)
                )
            );

            if (!transResponse.ok) {
                throw new Error('Failed to fetch transcription');
            }

            this.transcription = await transResponse.json();

            // Fetch summary
            const summaryResponse = await fetch(
                window.API_CONFIG.getFullUrl(
                    window.API_CONFIG.ENDPOINTS.SUMMARY(this.jobId)
                )
            );

            if (!summaryResponse.ok) {
                throw new Error('Failed to fetch summary');
            }

            this.summary = await summaryResponse.json();

            // Display results
            this.displayTranscription();
            this.displaySummary();
            this.displayActionItems();

            console.log('✅ Results loaded successfully');

        } catch (error) {
            console.error('Error loading results:', error);
            alert('Failed to load results: ' + error.message);
        }
    }

    displayTranscription() {
        const container = document.querySelector('.transcription-item').parentElement;
        container.innerHTML = '';

        if (!this.transcription || !this.transcription.segments) {
            container.innerHTML = '<p class="text-slate-500">No transcription available</p>';
            return;
        }

        this.transcription.segments.forEach(segment => {
            const div = document.createElement('div');
            div.className = 'transcription-item flex flex-col gap-2 text-sm';
            div.innerHTML = `
                <span class="font-bold text-primary cursor-pointer hover:underline">[${this.formatTime(segment.start || 0)}]</span>
                <p class="text-slate-500 dark:text-gray-300">
                    <span class="font-semibold text-slate-800 dark:text-white">${segment.speaker || 'Speaker'}:</span>
                    ${segment.text}
                </p>
            `;
            container.appendChild(div);
        });
    }

    displaySummary() {
        const summaryContent = document.getElementById('summary-content');
        
        if (!this.summary) {
            summaryContent.innerHTML = '<p class="text-slate-500">No summary available</p>';
            return;
        }

        let html = `<p>${this.summary.executive_summary || ''}</p>`;

        if (this.summary.main_topics && this.summary.main_topics.length > 0) {
            html += '<ul class="space-y-2 list-disc list-inside mt-4">';
            this.summary.main_topics.forEach(topic => {
                html += `<li>${topic}</li>`;
            });
            html += '</ul>';
        }

        if (this.summary.key_decisions && this.summary.key_decisions.length > 0) {
            html += '<h3 class="font-bold text-slate-800 dark:text-white mt-4 mb-2">Key Decisions</h3>';
            html += '<ul class="space-y-2 list-disc list-inside">';
            this.summary.key_decisions.forEach(decision => {
                html += `<li>${decision.decision || decision}</li>`;
            });
            html += '</ul>';
        }

        summaryContent.innerHTML = html;
    }

    displayActionItems() {
        const container = document.getElementById('action-items-list');
        container.innerHTML = '';

        if (!this.summary || !this.summary.action_items || this.summary.action_items.length === 0) {
            container.innerHTML = '<p class="text-slate-500 text-sm">No action items found</p>';
            return;
        }

        this.summary.action_items.forEach(item => {
            const priorityColors = {
                'urgent': 'bg-red-500',
                'high': 'bg-orange-500',
                'medium': 'bg-yellow-500',
                'normal': 'bg-blue-500',
                'low': 'bg-green-500'
            };

            const color = priorityColors[item.priority?.toLowerCase()] || 'bg-blue-500';

            const div = document.createElement('div');
            div.className = 'action-item flex items-start gap-3 p-3 rounded-lg bg-background-light dark:bg-background-dark';
            div.innerHTML = `
                <input class="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" 
                       type="checkbox" 
                       ${item.completed ? 'checked' : ''}/>
                <label class="flex-1 text-sm text-slate-800 dark:text-white ${item.completed ? 'line-through text-slate-500' : ''}">
                    ${item.description || item}
                </label>
                <div class="size-2.5 rounded-full ${color} mt-1.5 shrink-0" title="${item.priority || 'Normal'} Priority"></div>
            `;
            container.appendChild(div);
        });
    }

    setupEventListeners() {
        // Copy summary
        const copyBtn = document.getElementById('copy-summary-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copySummary());
        }

        // Regenerate summary
        const regenerateBtn = document.getElementById('regenerate-summary-btn');
        if (regenerateBtn) {
            regenerateBtn.addEventListener('click', () => this.regenerateSummary());
        }

        // Export all
        const exportAllBtn = document.getElementById('export-all-btn');
        if (exportAllBtn) {
            exportAllBtn.addEventListener('click', () => this.exportAll());
        }

        // Export actions
        const exportActionsBtn = document.getElementById('export-actions-btn');
        if (exportActionsBtn) {
            exportActionsBtn.addEventListener('click', () => this.exportActions());
        }
    }

    async copySummary() {
        if (!this.summary) return;

        const text = this.summary.executive_summary || '';
        try {
            await navigator.clipboard.writeText(text);
            alert('Summary copied to clipboard!');
        } catch (error) {
            console.error('Failed to copy:', error);
        }
    }

    async regenerateSummary() {
        const types = ['client_friendly', 'lawyer_professional', 'executive'];
        const choice = prompt('Choose summary type:\n1. Client Friendly\n2. Lawyer Professional\n3. Executive\n\nEnter number (1-3):');
        
        if (!choice || choice < 1 || choice > 3) return;

        const summaryType = types[parseInt(choice) - 1];

        try {
            const response = await fetch(
                window.API_CONFIG.getFullUrl(
                    window.API_CONFIG.ENDPOINTS.SUMMARY_REGENERATE(this.jobId)
                ) + `?summary_type=${summaryType}`,
                { method: 'POST' }
            );

            if (!response.ok) {
                throw new Error('Failed to regenerate summary');
            }

            this.summary = await response.json();
            this.displaySummary();
            this.displayActionItems();

            alert('Summary regenerated successfully!');

        } catch (error) {
            console.error('Regeneration error:', error);
            alert('Failed to regenerate summary');
        }
    }

    exportAll() {
        // Export transcript as PDF
        const transcriptUrl = window.API_CONFIG.getFullUrl(
            window.API_CONFIG.ENDPOINTS.TRANSCRIBE_DOWNLOAD(this.jobId, 'pdf')
        );
        window.open(transcriptUrl, '_blank');

        // Export summary as PDF
        setTimeout(() => {
            const summaryUrl = window.API_CONFIG.getFullUrl(
                window.API_CONFIG.ENDPOINTS.SUMMARY_EXPORT(this.jobId, 'pdf')
            );
            window.open(summaryUrl, '_blank');
        }, 500);
    }

    exportActions() {
        // Export summary which includes action items
        const url = window.API_CONFIG.getFullUrl(
            window.API_CONFIG.ENDPOINTS.SUMMARY_EXPORT(this.jobId, 'pdf')
        );
        window.open(url, '_blank');
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.resultsManager = new ResultsManager();
    });
} else {
    window.resultsManager = new ResultsManager();
}
