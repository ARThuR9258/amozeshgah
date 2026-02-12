/**
 * Modern Toaster Library for Django Messages
 * Converts Django messages into modern toast notifications
 */

class Toaster {
    constructor(options = {}) {
        this.options = {
            position: 'top-right',
            duration: 5000,
            closeOnClick: true,
            showProgress: true,
            ...options
        };
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.processDjangoMessages();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = `toaster-container toaster-${this.options.position}`;
        this.container.style.cssText = `
            position: fixed;
            z-index: 9999;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding: 20px;
            ${this.getPositionStyles()}
        `;
        document.body.appendChild(this.container);
    }

    getPositionStyles() {
        const positions = {
            'top-right': 'top: 0; right: 0;',
            'top-left': 'top: 0; left: 0;',
            'bottom-right': 'bottom: 0; right: 0;',
            'bottom-left': 'bottom: 0; left: 0;',
            'top-center': 'top: 0; left: 50%; transform: translateX(-50%);',
            'bottom-center': 'bottom: 0; left: 50%; transform: translateX(-50%);'
        };
        return positions[this.options.position] || positions['top-right'];
    }

    processDjangoMessages() {
        // Process Django messages if they exist
        const messages = document.querySelectorAll('.messages .message');
        messages.forEach(message => {
            const text = message.textContent.trim();
            const type = this.getMessageType(message);
            this.show(text, type);
            message.remove(); // Remove original Django message
        });
    }

    getMessageType(messageElement) {
        const classList = messageElement.className;
        if (classList.includes('success')) return 'success';
        if (classList.includes('error')) return 'error';
        if (classList.includes('warning')) return 'warning';
        if (classList.includes('info')) return 'info';
        return 'info';
    }

    show(message, type = 'info', options = {}) {
        const toast = this.createToast(message, type, options);
        this.container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Auto remove
        const duration = options.duration || this.options.duration;
        if (duration > 0) {
            setTimeout(() => {
                this.remove(toast);
            }, duration);
        }

        return toast;
    }

    createToast(message, type, options) {
        const toast = document.createElement('div');
        toast.className = `toaster-toast toaster-${type}`;
        
        const icon = this.getIcon(type);
        const hasProgress = options.showProgress !== false && this.options.showProgress;
        
        toast.innerHTML = `
            <div class="toaster-content">
                <div class="toaster-icon">${icon}</div>
                <div class="toaster-message">${message}</div>
                <button class="toaster-close">&times;</button>
            </div>
            ${hasProgress ? '<div class="toaster-progress"></div>' : ''}
        `;

        toast.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            padding: 16px;
            min-width: 300px;
            max-width: 400px;
            pointer-events: auto;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            border-right: 4px solid ${this.getTypeColor(type)};
        `;

        // Add event listeners
        const closeBtn = toast.querySelector('.toaster-close');
        closeBtn.addEventListener('click', () => this.remove(toast));

        if (this.options.closeOnClick) {
            toast.addEventListener('click', () => this.remove(toast));
        }

        // Animate progress bar
        if (hasProgress) {
            const progressBar = toast.querySelector('.toaster-progress');
            const duration = options.duration || this.options.duration;
            progressBar.style.cssText = `
                height: 3px;
                background: ${this.getTypeColor(type)};
                border-radius: 0 0 4px 4px;
                animation: progress ${duration}ms linear;
            `;
        }

        return toast;
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    getTypeColor(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        return colors[type] || colors.info;
    }

    remove(toast) {
        toast.classList.add('hide');
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Static methods for easy access
    static success(message, options = {}) {
        return window.toaster.show(message, 'success', options);
    }

    static error(message, options = {}) {
        return window.toaster.show(message, 'error', options);
    }

    static warning(message, options = {}) {
        return window.toaster.show(message, 'warning', options);
    }

    static info(message, options = {}) {
        return window.toaster.show(message, 'info', options);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    .toaster-toast.show {
        transform: translateX(0) !important;
        opacity: 1 !important;
    }

    .toaster-toast.hide {
        transform: translateX(100%) !important;
        opacity: 0 !important;
    }

    .toaster-content {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .toaster-icon {
        font-size: 20px;
        font-weight: bold;
        color: ${window.toaster ? window.toaster.getTypeColor('success') : '#10b981'};
        flex-shrink: 0;
    }

    .toaster-message {
        flex: 1;
        font-size: 14px;
        line-height: 1.4;
        color: #374151;
    }

    .toaster-close {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #9ca3af;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: background-color 0.2s;
    }

    .toaster-close:hover {
        background-color: #f3f4f6;
        color: #6b7280;
    }

    @keyframes progress {
        from {
            width: 100%;
        }
        to {
            width: 0%;
        }
    }

    /* RTL support */
    .toaster-container.toaster-top-right {
        direction: rtl;
    }

    .toaster-container.toaster-top-left {
        direction: ltr;
    }

    .toaster-container.toaster-bottom-right {
        direction: rtl;
    }

    .toaster-container.toaster-bottom-left {
        direction: ltr;
    }
`;
document.head.appendChild(style);

// Initialize toaster when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.toaster = new Toaster({
        position: 'top-left',
        duration: 4000,
        closeOnClick: true,
        showProgress: true
    });
});

// Global functions for easy access from Django templates
window.showToast = function(message, type = 'info', options = {}) {
    if (window.toaster) {
        return window.toaster.show(message, type, options);
    }
};

window.showSuccessToast = function(message, options = {}) {
    return window.showToast(message, 'success', options);
};

window.showErrorToast = function(message, options = {}) {
    return window.showToast(message, 'error', options);
};

window.showWarningToast = function(message, options = {}) {
    return window.showToast(message, 'warning', options);
};

window.showInfoToast = function(message, options = {}) {
    return window.showToast(message, 'info', options);
};
