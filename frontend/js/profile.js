/**
 * TranscribeAI - Profile Manager
 * Handles user profile management, photo uploads, and account settings
 */

class ProfileManager {
    constructor() {
        this.profile = {
            fullName: '',
            email: '',
            avatar: ''
        };
        this.init();
    }

    /**
     * Initialize profile manager
     */
    init() {
        this.loadProfile();
        this.setupTabs();
        this.setupPhotoUpload();
        this.setupProfileForm();
        this.setupDeleteAccount();
    }

    /**
     * Load profile data
     */
    loadProfile() {
        // Load from localStorage or API
        const saved = localStorage.getItem('user_profile');
        if (saved) {
            try {
                this.profile = JSON.parse(saved);
            } catch (e) {
                console.error('Error loading profile:', e);
            }
        } else {
            // Default profile
            this.profile = {
                fullName: 'Alex Chen',
                email: 'alex.chen@email.com',
                avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDMO51a7okLRYOa0ogS1tFL-DzHd6ACb6hRJFezngrFX-ynVudlc0pykY-jR_dCHsjRy7Jz90hUsJdjIhkhqlUe5scCyOPuvlj2-J5GUyAusIChjWWpGRu8hJawNKRX9L8VZifeiJEqiTDFd9QyOIR8-NTbxA0gHCxoWrYJXx0hy5wyGFhMm-_ONVc7qc1ifS4uSVW5gvIMUihF8SBEUgH-TMzxtNwA0DI4mZIGO08RNXl7II4lzVniICGX7ZrrEi8fgWPmk0qA20I'
            };
        }

        this.updateProfileUI();
    }

    /**
     * Update profile UI elements
     */
    updateProfileUI() {
        const displayName = document.getElementById('profile-display-name');
        const displayEmail = document.getElementById('profile-display-email');
        const inputName = document.getElementById('input-fullname');
        const inputEmail = document.getElementById('input-email');
        const avatar = document.getElementById('profile-avatar');

        if (displayName) displayName.textContent = this.profile.fullName;
        if (displayEmail) displayEmail.textContent = this.profile.email;
        if (inputName) inputName.value = this.profile.fullName;
        if (inputEmail) inputEmail.value = this.profile.email;
        if (avatar && this.profile.avatar) {
            avatar.style.backgroundImage = `url(${this.profile.avatar})`;
        }
    }

    /**
     * Set up tab navigation
     */
    setupTabs() {
        const tabLinks = document.querySelectorAll('.tab-link');
        
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = link.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        // Update tab links
        const tabLinks = document.querySelectorAll('.tab-link');
        tabLinks.forEach(link => {
            const linkTab = link.getAttribute('data-tab');
            if (linkTab === tabName) {
                link.classList.remove('border-b-transparent', 'text-gray-500', 'dark:text-gray-400');
                link.classList.add('border-b-primary', 'text-primary');
            } else {
                link.classList.add('border-b-transparent', 'text-gray-500', 'dark:text-gray-400');
                link.classList.remove('border-b-primary', 'text-primary');
            }
        });

        // Update tab content
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            const contentId = content.id.replace('content-', '');
            if (contentId === tabName) {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
            }
        });

        console.log('Switched to tab:', tabName);
    }

    /**
     * Set up photo upload
     */
    setupPhotoUpload() {
        const uploadBtn = document.getElementById('upload-photo-btn');
        const fileInput = document.getElementById('photo-upload-input');

        if (!uploadBtn || !fileInput) return;

        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadPhoto(file);
            }
        });
    }

    /**
     * Upload photo
     */
    uploadPhoto(file) {
        // Validate file
        if (!file.type.startsWith('image/')) {
            this.showToast('Please select an image file', 'error');
            return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            this.showToast('Image must be less than 5MB', 'error');
            return;
        }

        // Read and display image
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageUrl = e.target.result;
            this.profile.avatar = imageUrl;
            
            const avatar = document.getElementById('profile-avatar');
            if (avatar) {
                avatar.style.backgroundImage = `url(${imageUrl})`;
            }

            this.saveProfile();
            this.showToast('Photo uploaded successfully', 'success');
        };

        reader.readAsDataURL(file);
    }

    /**
     * Set up profile form
     */
    setupProfileForm() {
        const saveBtn = document.getElementById('save-profile-btn');
        const cancelBtn = document.getElementById('cancel-profile-btn');
        const form = document.getElementById('profile-form');

        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveProfileChanges();
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.cancelProfileChanges();
            });
        }

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveProfileChanges();
            });
        }
    }

    /**
     * Save profile changes
     */
    saveProfileChanges() {
        const nameInput = document.getElementById('input-fullname');
        const emailInput = document.getElementById('input-email');

        if (!nameInput || !emailInput) return;

        const newName = nameInput.value.trim();
        const newEmail = emailInput.value.trim();

        // Validation
        if (!newName) {
            this.showToast('Name cannot be empty', 'error');
            return;
        }

        if (!this.isValidEmail(newEmail)) {
            this.showToast('Please enter a valid email', 'error');
            return;
        }

        // Update profile
        this.profile.fullName = newName;
        this.profile.email = newEmail;

        this.saveProfile();
        this.updateProfileUI();
        this.showToast('Profile updated successfully', 'success');
    }

    /**
     * Cancel profile changes
     */
    cancelProfileChanges() {
        this.updateProfileUI();
        this.showToast('Changes cancelled', 'info');
    }

    /**
     * Validate email
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Save profile to storage
     */
    saveProfile() {
        try {
            localStorage.setItem('user_profile', JSON.stringify(this.profile));
            console.log('Profile saved:', this.profile);
        } catch (e) {
            console.error('Error saving profile:', e);
        }
    }

    /**
     * Set up account deletion
     */
    setupDeleteAccount() {
        const deleteBtn = document.getElementById('delete-account-btn');

        if (!deleteBtn) return;

        deleteBtn.addEventListener('click', () => {
            this.deleteAccount();
        });
    }

    /**
     * Delete account with confirmation
     */
    deleteAccount() {
        const confirmation = confirm(
            'Are you sure you want to delete your account?\n\n' +
            'This will permanently delete:\n' +
            '• All your transcriptions\n' +
            '• All your recordings\n' +
            '• All your settings\n\n' +
            'This action cannot be undone.'
        );

        if (!confirmation) return;

        // Second confirmation
        const finalConfirmation = prompt(
            'To confirm deletion, please type "DELETE" in capital letters:'
        );

        if (finalConfirmation !== 'DELETE') {
            this.showToast('Account deletion cancelled', 'info');
            return;
        }

        // Perform deletion
        this.performAccountDeletion();
    }

    /**
     * Perform account deletion
     */
    performAccountDeletion() {
        // Clear all local storage
        localStorage.clear();
        
        // In production, call API to delete account
        console.log('Account deleted');

        this.showToast('Account deleted successfully', 'success');

        // Redirect to home or login page after delay
        setTimeout(() => {
            window.location.href = '../index.html';
        }, 2000);
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

// Initialize profile manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.profileManager = new ProfileManager();
    });
} else {
    window.profileManager = new ProfileManager();
}
