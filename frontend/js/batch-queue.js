/**
 * TranscribeAI - Batch Queue Manager
 * Handles batch file uploads, queue management, and progress tracking
 */

class BatchQueueManager {
    constructor() {
        this.queue = [];
        this.isPaused = false;
        this.init();
    }

    /**
     * Initialize batch queue manager
     */
    init() {
        this.setupFileUpload();
        this.setupBatchControls();
        this.setupRowActions();
        this.startProgressSimulation();
    }

    /**
     * Set up file upload functionality
     */
    setupFileUpload() {
        const dropZone = document.getElementById('batch-drop-zone');
        const fileInput = document.getElementById('batch-file-input');
        const browseBtn = document.getElementById('browse-batch-files');

        if (!dropZone || !fileInput || !browseBtn) return;

        // Browse button click
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.addFilesToQueue(files);
            fileInput.value = ''; // Reset input
        });

        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('border-primary', 'bg-primary/5');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('border-primary', 'bg-primary/5');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = Array.from(e.dataTransfer.files);
            this.addFilesToQueue(files);
        });
    }

    /**
     * Add files to the queue
     */
    addFilesToQueue(files) {
        const tableBody = document.getElementById('queue-table-body');
        
        if (!tableBody) return;

        files.forEach((file, index) => {
            const fileId = Date.now() + index;
            const fileExtension = file.name.split('.').pop().toLowerCase();
            const icon = ['mp4', 'mov', 'webm'].includes(fileExtension) ? 'videocam' : 'audio_file';
            
            const row = this.createQueueRow(fileId, file.name, icon);
            tableBody.appendChild(row);
            
            // Add to queue array
            this.queue.push({
                id: fileId,
                name: file.name,
                status: 'pending',
                progress: 0,
                file: file
            });
        });

        this.updateBatchProgress();
        console.log(`Added ${files.length} files to queue`);
    }

    /**
     * Create a queue table row
     */
    createQueueRow(fileId, fileName, icon) {
        const row = document.createElement('tr');
        row.className = 'border-b border-slate-200 dark:border-slate-800';
        row.setAttribute('data-file-id', fileId);
        
        row.innerHTML = `
            <td class="px-6 py-4 font-medium text-slate-900 dark:text-white">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-slate-500">${icon}</span>
                    <span>${fileName}</span>
                </div>
            </td>
            <td class="px-6 py-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-300">Pending</span>
            </td>
            <td class="px-6 py-4 text-slate-500 dark:text-slate-400">0%</td>
            <td class="px-6 py-4 text-right">
                <button class="action-btn p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400" data-action="cancel" title="Cancel">
                    <span class="material-symbols-outlined">cancel</span>
                </button>
            </td>
        `;
        
        return row;
    }

    /**
     * Set up batch control buttons
     */
    setupBatchControls() {
        const pauseBtn = document.getElementById('pause-all-btn');
        const cancelBtn = document.getElementById('cancel-all-btn');

        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                this.togglePauseAll();
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelAll();
            });
        }
    }

    /**
     * Toggle pause/resume all
     */
    togglePauseAll() {
        this.isPaused = !this.isPaused;
        const pauseBtn = document.getElementById('pause-all-btn');
        
        if (pauseBtn) {
            const icon = pauseBtn.querySelector('.material-symbols-outlined');
            const text = pauseBtn.querySelector('.truncate');
            
            if (this.isPaused) {
                icon.textContent = 'play_arrow';
                text.textContent = 'Resume All';
                console.log('Batch queue paused');
            } else {
                icon.textContent = 'pause';
                text.textContent = 'Pause All';
                console.log('Batch queue resumed');
            }
        }
    }

    /**
     * Cancel all files in queue
     */
    cancelAll() {
        if (!confirm('Are you sure you want to cancel all files in the queue?')) {
            return;
        }

        const tableBody = document.getElementById('queue-table-body');
        if (tableBody) {
            tableBody.innerHTML = '';
        }

        this.queue = [];
        this.updateBatchProgress();
        console.log('All files cancelled');
    }

    /**
     * Set up row action buttons
     */
    setupRowActions() {
        const tableBody = document.getElementById('queue-table-body');
        
        if (!tableBody) return;

        tableBody.addEventListener('click', (e) => {
            const btn = e.target.closest('.action-btn, button[title]');
            if (!btn) return;

            const row = btn.closest('tr');
            const fileId = row?.getAttribute('data-file-id');
            const action = btn.getAttribute('data-action') || btn.getAttribute('title')?.toLowerCase();

            if (fileId) {
                this.handleRowAction(fileId, action, row);
            }
        });
    }

    /**
     * Handle individual row actions
     */
    handleRowAction(fileId, action, row) {
        switch (action) {
            case 'cancel':
                this.cancelFile(fileId, row);
                break;
            case 'pause':
                this.pauseFile(fileId, row);
                break;
            case 'retry':
                this.retryFile(fileId, row);
                break;
            case 'delete':
                this.deleteFile(fileId, row);
                break;
            default:
                console.log(`Action ${action} for file ${fileId}`);
        }
    }

    /**
     * Cancel a specific file
     */
    cancelFile(fileId, row) {
        row.remove();
        this.queue = this.queue.filter(f => f.id !== parseInt(fileId));
        this.updateBatchProgress();
        console.log(`File ${fileId} cancelled`);
    }

    /**
     * Pause a specific file
     */
    pauseFile(fileId, row) {
        console.log(`File ${fileId} paused`);
        // In production, update status and UI
    }

    /**
     * Retry a failed file
     */
    retryFile(fileId, row) {
        console.log(`Retrying file ${fileId}`);
        // In production, restart processing
    }

    /**
     * Delete a file from queue
     */
    deleteFile(fileId, row) {
        if (confirm('Are you sure you want to delete this file?')) {
            this.cancelFile(fileId, row);
        }
    }

    /**
     * Update batch progress bar
     */
    updateBatchProgress() {
        const progressBar = document.getElementById('batch-progress-bar');
        const progressText = document.getElementById('batch-progress-text');
        
        if (!progressBar || !progressText) return;

        const total = this.queue.length;
        const completed = this.queue.filter(f => f.status === 'completed').length;
        const percentage = total > 0 ? (completed / total) * 100 : 0;

        progressBar.style.width = `${percentage}%`;
        
        const remaining = total - completed;
        const estimatedTime = remaining * 2; // 2 minutes per file estimate
        
        progressText.textContent = `${completed} of ${total} files complete - Est. time remaining: ${estimatedTime} minutes`;
    }

    /**
     * Simulate progress for demo
     */
    startProgressSimulation() {
        // This is just for demo purposes
        setInterval(() => {
            if (this.isPaused) return;

            const processingRows = document.querySelectorAll('[data-file-id="2"]');
            processingRows.forEach(row => {
                const progressBar = row.querySelector('.bg-primary');
                const progressText = row.querySelector('.text-xs');
                
                if (progressBar && progressText) {
                    let currentProgress = parseInt(progressBar.style.width) || 45;
                    currentProgress = Math.min(currentProgress + 1, 100);
                    
                    progressBar.style.width = `${currentProgress}%`;
                    progressText.textContent = `${currentProgress}%`;
                    
                    if (currentProgress >= 100) {
                        // Update to completed status
                        const statusBadge = row.querySelector('.inline-flex');
                        if (statusBadge) {
                            statusBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300';
                            statusBadge.textContent = 'Completed';
                        }
                    }
                }
            });
        }, 2000);
    }
}

// Initialize batch queue manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.batchQueueManager = new BatchQueueManager();
    });
} else {
    window.batchQueueManager = new BatchQueueManager();
}
