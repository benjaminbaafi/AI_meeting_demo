/**
 * TranscribeAI - Permissions Manager
 * Handles sharing permissions, user invites, and access control
 */

class PermissionsManager {
    constructor() {
        this.collaborators = [];
        this.generalAccess = 'public';
        this.shareUrl = '';
        this.init();
    }

    /**
     * Initialize permissions manager
     */
    init() {
        this.generateShareUrl();
        this.loadCollaborators();
        this.setupInviteSystem();
        this.setupRoleSelectors();
        this.setupGeneralAccess();
        this.setupFooterButtons();
        this.setupCloseButton();
    }

    /**
     * Generate share URL
     */
    generateShareUrl() {
        const baseUrl = window.location.origin;
        const fileId = 'project-kickoff-meeting';
        this.shareUrl = `${baseUrl}/share/${fileId}`;
    }

    /**
     * Load existing collaborators
     */
    loadCollaborators() {
        // In production, load from API
        this.collaborators = [
            {
                id: 'user-1',
                name: 'Benjamin Carter',
                email: 'ben.carter@example.com',
                role: 'editor',
                avatar: 'https://via.placeholder.com/40'
            },
            {
                id: 'user-2',
                name: 'Olivia Rodriguez',
                email: 'olivia.r@example.com',
                role: 'viewer',
                avatar: 'https://via.placeholder.com/40'
            }
        ];
    }

    /**
     * Set up invite system
     */
    setupInviteSystem() {
        const inviteBtn = document.getElementById('invite-btn');
        const emailInput = document.getElementById('invite-email-input');
        const roleSelect = document.getElementById('invite-role-select');

        if (!inviteBtn || !emailInput || !roleSelect) return;

        inviteBtn.addEventListener('click', () => {
            const email = emailInput.value.trim();
            const role = roleSelect.value;

            if (!email) {
                this.showToast('Please enter an email address', 'error');
                return;
            }

            if (!this.isValidEmail(email)) {
                this.showToast('Please enter a valid email address', 'error');
                return;
            }

            this.inviteUser(email, role);
            emailInput.value = '';
        });

        // Handle Enter key in email input
        emailInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                inviteBtn.click();
            }
        });
    }

    /**
     * Validate email address
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Invite a new user
     */
    inviteUser(email, role) {
        // Check if user already has access
        const existing = this.collaborators.find(c => c.email === email);
        if (existing) {
            this.showToast('User already has access', 'error');
            return;
        }

        // Add new collaborator
        const newCollaborator = {
            id: `user-${Date.now()}`,
            name: email.split('@')[0], // Use email prefix as name for now
            email: email,
            role: role,
            avatar: 'https://via.placeholder.com/40' // Default avatar
        };

        this.collaborators.push(newCollaborator);
        this.addCollaboratorToUI(newCollaborator);
        this.showToast(`Invited ${email} as ${role}`, 'success');

        console.log('User invited:', newCollaborator);
    }

    /**
     * Add collaborator to UI
     */
    addCollaboratorToUI(collaborator) {
        const list = document.getElementById('collaborators-list');
        if (!list) return;

        const item = document.createElement('div');
        item.className = 'flex items-center gap-4 bg-transparent min-h-[64px] py-2 justify-between collaborator-item fade-in';
        item.setAttribute('data-user-id', collaborator.id);
        item.setAttribute('data-role', collaborator.role);

        item.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="rounded-full h-10 w-10 bg-primary/20 flex items-center justify-center text-primary font-bold">
                    ${collaborator.name.charAt(0).toUpperCase()}
                </div>
                <div class="flex flex-col justify-center">
                    <p class="text-gray-900 dark:text-white text-sm font-medium leading-normal line-clamp-1">${collaborator.name}</p>
                    <p class="text-gray-500 dark:text-gray-400 text-sm font-normal leading-normal line-clamp-2">${collaborator.email}</p>
                </div>
            </div>
            <div class="relative shrink-0 role-selector-container">
                <select class="role-select form-select flex w-full cursor-pointer items-center justify-between overflow-hidden rounded-lg h-10 px-4 bg-gray-100 dark:bg-gray-800/50 text-gray-900 dark:text-white text-sm font-medium leading-normal border-gray-300 dark:border-gray-700 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-0 focus:ring-2 focus:ring-primary/50 appearance-none pr-10">
                    <option value="editor" ${collaborator.role === 'editor' ? 'selected' : ''}>Editor</option>
                    <option value="viewer" ${collaborator.role === 'viewer' ? 'selected' : ''}>Viewer</option>
                    <option value="remove">Remove access</option>
                </select>
                <span class="material-symbols-outlined pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">expand_more</span>
            </div>
        `;

        list.appendChild(item);
        this.setupRoleSelector(item);
    }

    /**
     * Set up role selectors for all collaborators
     */
    setupRoleSelectors() {
        const items = document.querySelectorAll('.collaborator-item');
        items.forEach(item => this.setupRoleSelector(item));
    }

    /**
     * Set up individual role selector
     */
    setupRoleSelector(item) {
        const select = item.querySelector('.role-select');
        if (!select) return;

        select.addEventListener('change', (e) => {
            const newRole = e.target.value;
            const userId = item.getAttribute('data-user-id');
            const userName = item.querySelector('.text-sm.font-medium').textContent;

            if (newRole === 'remove') {
                this.removeCollaborator(userId, userName, item);
                e.target.value = item.getAttribute('data-role'); // Reset select
            } else {
                this.updateCollaboratorRole(userId, newRole, userName);
                item.setAttribute('data-role', newRole);
            }
        });
    }

    /**
     * Update collaborator role
     */
    updateCollaboratorRole(userId, newRole, userName) {
        const collaborator = this.collaborators.find(c => c.id === userId);
        if (collaborator) {
            collaborator.role = newRole;
            this.showToast(`Changed ${userName}'s role to ${newRole}`, 'success');
            console.log('Role updated:', userId, newRole);
        }
    }

    /**
     * Remove collaborator
     */
    removeCollaborator(userId, userName, itemElement) {
        if (!confirm(`Remove ${userName}'s access to this file?`)) {
            return;
        }

        this.collaborators = this.collaborators.filter(c => c.id !== userId);
        itemElement.remove();
        this.showToast(`Removed ${userName}'s access`, 'success');
        console.log('Collaborator removed:', userId);
    }

    /**
     * Set up general access selector
     */
    setupGeneralAccess() {
        const select = document.getElementById('general-access-select');
        const description = document.getElementById('general-access-description');

        if (!select || !description) return;

        select.addEventListener('change', (e) => {
            const newAccess = e.target.value;
            this.generalAccess = newAccess;

            if (newAccess === 'public') {
                description.textContent = 'Anyone on the internet with this link can view. No sign-in required.';
            } else {
                description.textContent = 'Only people with access can open with the link.';
            }

            this.showToast(`General access changed to ${newAccess}`, 'success');
            console.log('General access updated:', newAccess);
        });
    }

    /**
     * Set up footer buttons
     */
    setupFooterButtons() {
        const copyBtn = document.getElementById('copy-link-btn-footer');
        const doneBtn = document.getElementById('done-btn');

        if (copyBtn) {
            copyBtn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(this.shareUrl);
                    this.showCopySuccess(copyBtn);
                } catch (err) {
                    console.error('Copy failed:', err);
                    this.showToast('Failed to copy link', 'error');
                }
            });
        }

        if (doneBtn) {
            doneBtn.addEventListener('click', () => {
                this.closeModal();
            });
        }
    }

    /**
     * Show copy success feedback
     */
    showCopySuccess(button) {
        const originalHTML = button.innerHTML;
        
        button.innerHTML = `
            <span class="material-symbols-outlined text-base">check</span>
            <span class="truncate">Copied!</span>
        `;

        setTimeout(() => {
            button.innerHTML = originalHTML;
        }, 2000);
    }

    /**
     * Set up close button
     */
    setupCloseButton() {
        const closeBtn = document.getElementById('close-permissions-modal');
        
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
     * Close the modal
     */
    closeModal() {
        // Save permissions before closing
        this.savePermissions();
        
        // Navigate back or to results page
        if (document.referrer) {
            window.history.back();
        } else {
            window.location.href = 'results.html';
        }
    }

    /**
     * Save permissions
     */
    savePermissions() {
        const permissions = {
            collaborators: this.collaborators,
            generalAccess: this.generalAccess,
            lastUpdated: new Date().toISOString()
        };

        // In production, save to API
        console.log('Permissions saved:', permissions);
        localStorage.setItem('file_permissions', JSON.stringify(permissions));
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

// Initialize permissions manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.permissionsManager = new PermissionsManager();
    });
} else {
    window.permissionsManager = new PermissionsManager();
}
