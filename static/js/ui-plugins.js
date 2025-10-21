/**
 * UI Plugins Manager
 * Handles modern UI enhancements: toast notifications, loading animations, and smooth transitions
 */

class UIPlugins {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    init() {
        this.createToastContainer();
        this.addLoadingStyles();
    }

    /**
     * Create toast notification container
     */
    createToastContainer() {
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = 'toast-container';
            document.body.appendChild(this.toastContainer);
        }
    }

    /**
     * Show toast notification
     * @param {string} message - The message to display
     * @param {string} type - success, error, warning, info
     * @param {number} duration - Duration in milliseconds
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} toast-enter`;

        const icon = this.getIconForType(type);
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        this.toastContainer.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('toast-show'), 10);

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('toast-show');
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Get icon for toast type
     */
    getIconForType(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    /**
     * Show loading overlay
     * @param {string} message - Loading message
     */
    showLoading(message = 'Loading...') {
        let loader = document.getElementById('ui-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'ui-loader';
            loader.className = 'ui-loader';
            document.body.appendChild(loader);
        }

        loader.innerHTML = `
            <div class="ui-loader-content">
                <div class="spinner"></div>
                <div class="loader-message">${message}</div>
            </div>
        `;
        loader.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        const loader = document.getElementById('ui-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    /**
     * Add smooth fade-in animation to element
     */
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';

        let opacity = 0;
        const interval = 10;
        const increment = interval / duration;

        const timer = setInterval(() => {
            opacity += increment;
            element.style.opacity = opacity;
            if (opacity >= 1) {
                clearInterval(timer);
                element.style.opacity = '1';
            }
        }, interval);
    }

    /**
     * Add smooth fade-out animation to element
     */
    fadeOut(element, duration = 300) {
        let opacity = 1;
        const interval = 10;
        const decrement = interval / duration;

        const timer = setInterval(() => {
            opacity -= decrement;
            element.style.opacity = opacity;
            if (opacity <= 0) {
                clearInterval(timer);
                element.style.display = 'none';
                element.style.opacity = '0';
            }
        }, interval);
    }

    /**
     * Add loading styles dynamically
     */
    addLoadingStyles() {
        if (document.getElementById('ui-plugins-styles')) return;

        const style = document.createElement('style');
        style.id = 'ui-plugins-styles';
        style.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }

            .toast {
                display: flex;
                align-items: center;
                min-width: 300px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(400px);
                transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }

            .toast-show {
                transform: translateX(0);
            }

            .toast-exit {
                opacity: 0;
                transform: translateX(400px);
            }

            .toast-icon {
                font-size: 24px;
                margin-right: 12px;
                font-weight: bold;
            }

            .toast-message {
                flex: 1;
                font-family: 'Raleway', sans-serif;
                font-size: 14px;
            }

            .toast-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                margin-left: 10px;
                color: #666;
                transition: color 0.2s;
            }

            .toast-close:hover {
                color: #000;
            }

            .toast-success {
                border-left: 4px solid #28a745;
            }

            .toast-success .toast-icon {
                color: #28a745;
            }

            .toast-error {
                border-left: 4px solid #dc3545;
            }

            .toast-error .toast-icon {
                color: #dc3545;
            }

            .toast-warning {
                border-left: 4px solid #ffc107;
            }

            .toast-warning .toast-icon {
                color: #ffc107;
            }

            .toast-info {
                border-left: 4px solid #17a2b8;
            }

            .toast-info .toast-icon {
                color: #17a2b8;
            }

            .ui-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }

            .ui-loader-content {
                text-align: center;
                color: white;
            }

            .spinner {
                width: 50px;
                height: 50px;
                margin: 0 auto 20px;
                border: 5px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            .loader-message {
                font-family: 'Raleway', sans-serif;
                font-size: 16px;
            }

            /* Smooth transitions for all interactive elements */
            button, .btn, input, select, textarea {
                transition: all 0.2s ease-in-out;
            }

            button:hover, .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            button:active, .btn:active {
                transform: translateY(0);
            }

            /* Card hover effects */
            .card, .service-card {
                transition: all 0.3s ease;
            }

            .card:hover {
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }

            /* Pulse animation for status indicators */
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .status-indicator.pulse {
                animation: pulse 2s ease-in-out infinite;
            }

            /* Fade in animation */
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* Slide in animation */
            .slide-in {
                animation: slideIn 0.5s ease-out;
            }

            @keyframes slideIn {
                from { transform: translateX(-100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize DataTable if available
     * @param {string} tableId - ID of table element
     * @param {Object} options - DataTable options
     */
    initDataTable(tableId, options = {}) {
        if (typeof jQuery !== 'undefined' && jQuery.fn.DataTable) {
            const defaultOptions = {
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']],
                language: {
                    search: "Filter:",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries"
                }
            };
            return jQuery(`#${tableId}`).DataTable({...defaultOptions, ...options});
        }
    }

    /**
     * Format bytes to human readable
     */
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize global UI instance
window.ui = new UIPlugins();