/**
 * TranscribeAI - Feature Tour Manager
 * Handles the onboarding/feature tour experience
 */

class TourManager {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            {
                features: [
                    { icon: 'mic', label: 'Record', active: true },
                    { icon: 'description', label: 'Transcribe', active: false },
                    { icon: 'summarize', label: 'Summarize', active: false }
                ],
                title: 'Effortless, Accurate Transcriptions',
                description: 'Upload any audio or video and receive a precise, time-stamped transcript in minutes.'
            },
            {
                features: [
                    { icon: 'auto_awesome', label: 'AI Analysis', active: true },
                    { icon: 'psychology', label: 'Smart Insights', active: false },
                    { icon: 'lightbulb', label: 'Key Points', active: false }
                ],
                title: 'Intelligent AI Summaries',
                description: 'Get concise summaries with key highlights, topics, and important moments automatically extracted.'
            },
            {
                features: [
                    { icon: 'task_alt', label: 'Action Items', active: true },
                    { icon: 'check_circle', label: 'Decisions', active: false },
                    { icon: 'flag', label: 'Follow-ups', active: false }
                ],
                title: 'Action Item Detection',
                description: 'Automatically identify tasks, decisions, and follow-up items discussed in your meetings.'
            }
        ];
        this.init();
    }

    /**
     * Initialize tour
     */
    init() {
        this.renderStep(this.currentStep);
        this.setupNavigation();
        this.setupDots();
    }

    /**
     * Render current step
     */
    renderStep(stepIndex) {
        const step = this.steps[stepIndex];
        const featureDisplay = document.getElementById('feature-display');
        const title = document.getElementById('tour-title');
        const description = document.getElementById('tour-description');
        const nextBtn = document.getElementById('next-btn');

        // Update title and description
        if (title) title.textContent = step.title;
        if (description) description.textContent = step.description;

        // Update next button text
        if (nextBtn) {
            if (stepIndex === this.steps.length - 1) {
                nextBtn.innerHTML = '<span class="truncate">Get Started</span>';
            } else {
                nextBtn.innerHTML = '<span class="truncate">Next</span>';
            }
        }

        // Render features
        if (featureDisplay) {
            featureDisplay.innerHTML = step.features.map((feature, index) => `
                <div class="flex flex-col items-center gap-4 text-center transition-all duration-500 ${feature.active ? 'scale-110' : 'scale-100 opacity-60'}">
                    <div class="flex size-14 items-center justify-center rounded-full ${feature.active ? 'bg-primary/20 text-primary' : 'bg-gray-100 text-gray-400'} dark:bg-primary/10 dark:text-primary-300 transition-all duration-500">
                        <span class="material-symbols-outlined text-4xl">${feature.icon}</span>
                    </div>
                    <h2 class="text-base font-semibold ${feature.active ? 'text-slate-800' : 'text-gray-500'} dark:text-gray-300">${feature.label}</h2>
                </div>
                ${index < step.features.length - 1 ? '<div class="h-full w-px bg-gray-200 dark:bg-white/10"></div>' : ''}
            `).join('');
        }

        // Update pagination dots
        this.updateDots(stepIndex);
    }

    /**
     * Update pagination dots
     */
    updateDots(activeIndex) {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            if (index === activeIndex) {
                dot.classList.remove('bg-gray-300', 'dark:bg-white/10');
                dot.classList.add('bg-primary');
            } else {
                dot.classList.add('bg-gray-300', 'dark:bg-white/10');
                dot.classList.remove('bg-primary');
            }
        });
    }

    /**
     * Set up navigation
     */
    setupNavigation() {
        const nextBtn = document.getElementById('next-btn');
        const skipBtn = document.getElementById('skip-btn');

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.nextStep();
            });
        }

        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                this.finish();
            });
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'Enter') {
                this.nextStep();
            } else if (e.key === 'ArrowLeft') {
                this.previousStep();
            } else if (e.key === 'Escape') {
                this.finish();
            }
        });
    }

    /**
     * Set up pagination dots
     */
    setupDots() {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.goToStep(index);
            });
        });
    }

    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.currentStep++;
            this.renderStep(this.currentStep);
        } else {
            this.finish();
        }
    }

    /**
     * Go to previous step
     */
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.renderStep(this.currentStep);
        }
    }

    /**
     * Go to specific step
     */
    goToStep(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.steps.length) {
            this.currentStep = stepIndex;
            this.renderStep(this.currentStep);
        }
    }

    /**
     * Finish tour
     */
    finish() {
        // Mark tour as completed
        localStorage.setItem('tour_completed', 'true');
        
        // Redirect to main app
        window.location.href = 'pages/upload.html';
    }
}

// Initialize tour when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.tourManager = new TourManager();
    });
} else {
    window.tourManager = new TourManager();
}
