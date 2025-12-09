/**
 * TranscribeAI - History Manager
 * Handles recent files sidebar, search, and file selection
 */

class HistoryManager {
    constructor() {
        this.files = [];
        this.filteredFiles = [];
        this.activeFileId = null;
        this.init();
    }

    /**
     * Initialize history manager
     */
    init() {
        this.setupSearch();
        this.setupFileItems();
        this.setupSidebarToggle();
        this.setupThemeToggle();
    }

    /**
     * Set up search functionality
     */
    setupSearch() {
        const searchInput = document.getElementById('history-search');
        
        if (!searchInput) return;
        
        searchInput.addEventListener('input', TranscribeAI.debounce((e) => {
            this.filterFiles(e.target.value);
        }, 300));
    }

    /**
     * Filter files based on search query
     */
    filterFiles(query) {
        const fileItems = document.querySelectorAll('.file-item');
        const lowerQuery = query.toLowerCase();
        
        fileItems.forEach(item => {
            const filename = item.getAttribute('data-filename')?.toLowerCase() || '';
            
            if (filename.includes(lowerQuery)) {
                item.style.display = 'flex';
                
                // Highlight matching text
                if (query) {
                    item.classList.add('search-match');
                } else {
                    item.classList.remove('search-match');
                }
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show "no results" message if needed
        const visibleItems = Array.from(fileItems).filter(item => item.style.display !== 'none');
        if (visibleItems.length === 0 && query) {
            this.showNoResults();
        } else {
            this.hideNoResults();
        }
    }

    /**
     * Show no results message
     */
    showNoResults() {
        const fileList = document.getElementById('file-list');
        
        if (!fileList) return;
        
        if (!document.getElementById('no-results')) {
            const noResults = document.createElement('div');
            noResults.id = 'no-results';
            noResults.className = 'text-center py-8';
            noResults.innerHTML = `
                <span class="material-symbols-outlined text-4xl text-gray-400 dark:text-gray-600">search_off</span>
                <p class="text-gray-500 dark:text-gray-400 text-sm mt-2">No files found</p>
            `;
            fileList.appendChild(noResults);
        }
    }

    /**
     * Hide no results message
     */
    hideNoResults() {
        const noResults = document.getElementById('no-results');
        if (noResults) {
            noResults.remove();
        }
    }

    /**
     * Set up file item click handlers
     */
    setupFileItems() {
        const fileItems = document.querySelectorAll('.file-item');
        
        fileItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't handle if it's an anchor link (first item)
                if (item.tagName === 'A') return;
                
                e.preventDefault();
                this.selectFile(item);
            });
        });
    }

    /**
     * Select a file and update UI
     */
    selectFile(item) {
        // Remove active state from all items
        const allItems = document.querySelectorAll('.file-item');
        allItems.forEach(i => {
            i.classList.remove('active');
        });
        
        // Add active state to selected item
        item.classList.add('active');
        
        const filename = item.getAttribute('data-filename');
        console.log('Selected file:', filename);
        
        // Update main content area
        this.loadFileContent(filename);
    }

    /**
     * Load file content in main area
     */
    loadFileContent(filename) {
        const mainContent = document.querySelector('main');
        
        if (!mainContent) return;
        
        // For demo, just show a message
        // In production, this would load actual transcription data
        mainContent.innerHTML = `
            <div class="max-w-4xl mx-auto fade-in">
                <div class="mb-6">
                    <a href="history.html" class="text-primary hover:underline text-sm">&larr; Back to History</a>
                </div>
                <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-4">${filename}</h1>
                <div class="card p-6 mb-6">
                    <h2 class="text-xl font-bold mb-4">File Details</h2>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Status</p>
                            <p class="text-gray-800 dark:text-white font-medium">Processed</p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Duration</p>
                            <p class="text-gray-800 dark:text-white font-medium">45:32</p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">File Size</p>
                            <p class="text-gray-800 dark:text-white font-medium">124 MB</p>
                        </div>
                        <div>
                            <p class="text-gray-500 dark:text-gray-400">Format</p>
                            <p class="text-gray-800 dark:text-white font-medium">${filename.split('.').pop().toUpperCase()}</p>
                        </div>
                    </div>
                </div>
                <div class="flex gap-4">
                    <a href="results.html" class="btn btn-primary">View Full Results</a>
                    <button class="btn btn-secondary">Download Transcript</button>
                </div>
            </div>
        `;
    }

    /**
     * Set up sidebar toggle
     */
    setupSidebarToggle() {
        const toggleBtn = document.getElementById('toggle-sidebar');
        const sidebar = document.querySelector('aside');
        
        if (!toggleBtn || !sidebar) return;
        
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            
            const icon = toggleBtn.querySelector('.material-symbols-outlined');
            if (sidebar.classList.contains('collapsed')) {
                icon.textContent = 'last_page';
                sidebar.style.width = '4rem';
            } else {
                icon.textContent = 'first_page';
                sidebar.style.width = '20rem';
            }
        });
    }

    /**
     * Set up theme toggle
     */
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle-history');
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                window.themeManager.toggle();
            });
        }
    }
}

// Add CSS for file items
const style = document.createElement('style');
style.textContent = `
    .file-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        background-color: transparent;
        padding: 0.5rem 0.75rem;
        min-height: 72px;
        justify-content: space-between;
        border-radius: 0.5rem;
        position: relative;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .file-item:hover {
        background-color: rgba(243, 244, 246, 1);
    }
    
    .dark .file-item:hover {
        background-color: rgba(31, 41, 55, 0.5);
    }
    
    .file-item.active {
        background-color: rgba(36, 99, 235, 0.1);
    }
    
    .dark .file-item.active {
        background-color: rgba(36, 99, 235, 0.2);
    }
    
    .file-item.search-match {
        background-color: rgba(255, 237, 213, 0.3);
    }
    
    .dark .file-item.search-match {
        background-color: rgba(255, 237, 213, 0.1);
    }
`;
document.head.appendChild(style);

// Initialize history manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.historyManager = new HistoryManager();
    });
} else {
    window.historyManager = new HistoryManager();
}
