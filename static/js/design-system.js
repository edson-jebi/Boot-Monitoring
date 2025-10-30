/**
 * Boot-Monitoring Design System JavaScript Utilities
 * Version: 1.0.0
 *
 * Provides interactive functionality for UI components
 */

(function() {
    'use strict';

    /**
     * Toast Notification System
     */
    class ToastManager {
        constructor() {
            this.container = this.createContainer();
            this.toasts = [];
        }

        createContainer() {
            let container = document.querySelector('.toast-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'toast-container';
                document.body.appendChild(container);
            }
            return container;
        }

        show(options) {
            const {
                type = 'info',
                title = '',
                message = '',
                duration = 5000,
                closeable = true
            } = options;

            const toast = this.createToast(type, title, message, closeable);
            this.container.appendChild(toast);
            this.toasts.push(toast);

            // Auto-dismiss after duration
            if (duration > 0) {
                setTimeout(() => {
                    this.dismiss(toast);
                }, duration);
            }

            return toast;
        }

        createToast(type, title, message, closeable) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'polite');

            const icon = this.getIcon(type);

            toast.innerHTML = `
                ${icon}
                <div class="toast-content">
                    ${title ? `<div class="toast-title">${this.escapeHtml(title)}</div>` : ''}
                    ${message ? `<div class="toast-message">${this.escapeHtml(message)}</div>` : ''}
                </div>
                ${closeable ? '<button class="toast-close" aria-label="Close">&times;</button>' : ''}
            `;

            if (closeable) {
                const closeBtn = toast.querySelector('.toast-close');
                closeBtn.addEventListener('click', () => this.dismiss(toast));
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
            return `<div class="toast-icon">${icons[type] || icons.info}</div>`;
        }

        dismiss(toast) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';

            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
                const index = this.toasts.indexOf(toast);
                if (index > -1) {
                    this.toasts.splice(index, 1);
                }
            }, 300);
        }

        dismissAll() {
            this.toasts.forEach(toast => this.dismiss(toast));
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    /**
     * Modal System
     */
    class Modal {
        constructor(element) {
            this.element = element;
            this.backdrop = null;
            this.isOpen = false;
            this.setupEventListeners();
        }

        setupEventListeners() {
            // Close on backdrop click
            this.element.addEventListener('click', (e) => {
                if (e.target === this.element) {
                    this.close();
                }
            });

            // Close button
            const closeButtons = this.element.querySelectorAll('[data-modal-close]');
            closeButtons.forEach(btn => {
                btn.addEventListener('click', () => this.close());
            });

            // Escape key to close
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }

        open() {
            this.isOpen = true;
            this.createBackdrop();
            this.element.style.display = 'block';
            document.body.style.overflow = 'hidden';

            // Focus trap
            this.trapFocus();

            this.element.dispatchEvent(new CustomEvent('modal:opened'));
        }

        close() {
            this.isOpen = false;
            this.element.style.display = 'none';

            if (this.backdrop) {
                this.backdrop.remove();
                this.backdrop = null;
            }

            document.body.style.overflow = '';
            this.element.dispatchEvent(new CustomEvent('modal:closed'));
        }

        createBackdrop() {
            this.backdrop = document.createElement('div');
            this.backdrop.className = 'modal-backdrop';
            this.backdrop.addEventListener('click', () => this.close());
            document.body.appendChild(this.backdrop);
        }

        trapFocus() {
            const focusableElements = this.element.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );

            if (focusableElements.length === 0) return;

            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            firstElement.focus();

            this.element.addEventListener('keydown', (e) => {
                if (e.key !== 'Tab') return;

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            });
        }
    }

    /**
     * Tabs System
     */
    class Tabs {
        constructor(element) {
            this.element = element;
            this.tabs = element.querySelectorAll('.nav-tab');
            this.panels = [];
            this.setupTabs();
        }

        setupTabs() {
            this.tabs.forEach((tab, index) => {
                const panelId = tab.getAttribute('data-tab-target');
                const panel = document.getElementById(panelId);

                if (panel) {
                    this.panels.push(panel);

                    tab.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.activateTab(index);
                    });

                    // Keyboard navigation
                    tab.addEventListener('keydown', (e) => {
                        let nextIndex;

                        if (e.key === 'ArrowRight') {
                            nextIndex = (index + 1) % this.tabs.length;
                        } else if (e.key === 'ArrowLeft') {
                            nextIndex = (index - 1 + this.tabs.length) % this.tabs.length;
                        } else if (e.key === 'Home') {
                            nextIndex = 0;
                        } else if (e.key === 'End') {
                            nextIndex = this.tabs.length - 1;
                        }

                        if (nextIndex !== undefined) {
                            e.preventDefault();
                            this.activateTab(nextIndex);
                            this.tabs[nextIndex].focus();
                        }
                    });
                }
            });

            // Activate first tab by default
            if (this.tabs.length > 0) {
                this.activateTab(0);
            }
        }

        activateTab(index) {
            // Deactivate all tabs and panels
            this.tabs.forEach((tab, i) => {
                tab.classList.remove('active');
                tab.setAttribute('aria-selected', 'false');
                tab.setAttribute('tabindex', '-1');

                if (this.panels[i]) {
                    this.panels[i].classList.remove('active');
                    this.panels[i].setAttribute('hidden', '');
                }
            });

            // Activate selected tab and panel
            this.tabs[index].classList.add('active');
            this.tabs[index].setAttribute('aria-selected', 'true');
            this.tabs[index].removeAttribute('tabindex');

            if (this.panels[index]) {
                this.panels[index].classList.add('active');
                this.panels[index].removeAttribute('hidden');
            }
        }
    }

    /**
     * Tooltip System
     */
    class Tooltip {
        constructor(element) {
            this.element = element;
            this.content = element.getAttribute('data-tooltip');
            this.position = element.getAttribute('data-tooltip-position') || 'top';
            this.tooltip = null;
            this.setupTooltip();
        }

        setupTooltip() {
            this.element.addEventListener('mouseenter', () => this.show());
            this.element.addEventListener('mouseleave', () => this.hide());
            this.element.addEventListener('focus', () => this.show());
            this.element.addEventListener('blur', () => this.hide());
        }

        show() {
            if (!this.content) return;

            this.tooltip = document.createElement('div');
            this.tooltip.className = `tooltip tooltip-${this.position}`;
            this.tooltip.textContent = this.content;
            this.tooltip.setAttribute('role', 'tooltip');

            document.body.appendChild(this.tooltip);
            this.positionTooltip();
        }

        hide() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        }

        positionTooltip() {
            const rect = this.element.getBoundingClientRect();
            const tooltipRect = this.tooltip.getBoundingClientRect();

            let top, left;

            switch (this.position) {
                case 'top':
                    top = rect.top - tooltipRect.height - 8;
                    left = rect.left + (rect.width - tooltipRect.width) / 2;
                    break;
                case 'bottom':
                    top = rect.bottom + 8;
                    left = rect.left + (rect.width - tooltipRect.width) / 2;
                    break;
                case 'left':
                    top = rect.top + (rect.height - tooltipRect.height) / 2;
                    left = rect.left - tooltipRect.width - 8;
                    break;
                case 'right':
                    top = rect.top + (rect.height - tooltipRect.height) / 2;
                    left = rect.right + 8;
                    break;
            }

            this.tooltip.style.top = `${top}px`;
            this.tooltip.style.left = `${left}px`;
        }
    }

    /**
     * Loading Overlay
     */
    function showLoading(element) {
        if (element.querySelector('.loading-overlay')) return;

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';

        element.style.position = 'relative';
        element.appendChild(overlay);
    }

    function hideLoading(element) {
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    /**
     * Confirmation Dialog
     */
    function confirm(options) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'warning'
        } = options;

        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal-backdrop';
            modal.innerHTML = `
                <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3 id="confirm-title" class="modal-title">${title}</h3>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer" style="display: flex; gap: var(--space-2); justify-content: flex-end;">
                            <button class="btn btn-secondary" data-action="cancel">${cancelText}</button>
                            <button class="btn btn-primary btn-${type}" data-action="confirm">${confirmText}</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';

            const confirmBtn = modal.querySelector('[data-action="confirm"]');
            const cancelBtn = modal.querySelector('[data-action="cancel"]');

            const cleanup = () => {
                modal.remove();
                document.body.style.overflow = '';
            };

            confirmBtn.addEventListener('click', () => {
                cleanup();
                resolve(true);
            });

            cancelBtn.addEventListener('click', () => {
                cleanup();
                resolve(false);
            });

            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    cleanup();
                    resolve(false);
                }
            });

            // Focus confirm button
            confirmBtn.focus();
        });
    }

    /**
     * Initialize all components
     */
    function init() {
        // Initialize modals
        document.querySelectorAll('[data-modal]').forEach(element => {
            new Modal(element);
        });

        // Initialize tabs
        document.querySelectorAll('.nav-tabs-modern').forEach(element => {
            new Tabs(element);
        });

        // Initialize tooltips
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            new Tooltip(element);
        });

        // Modal triggers
        document.querySelectorAll('[data-modal-open]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal-open');
                const modal = document.getElementById(modalId);
                if (modal && modal._modal) {
                    modal._modal.open();
                }
            });
        });
    }

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export to global scope
    window.DesignSystem = {
        toast: new ToastManager(),
        Modal,
        Tabs,
        Tooltip,
        showLoading,
        hideLoading,
        confirm,
        init
    };

})();
