/**
 * Service Monitor Module
 * Handles service status monitoring, control actions, and configuration management
 */

class ServiceMonitor {
    constructor() {
        this.lastUpdateTime = null;
        this.updateInterval = null;
        this.updateIntervalMs = 10000; // 10 seconds
    }

    /**
     * Initialize service monitor
     */
    init() {
        this.updateServiceStatus();
        this.startAutoUpdate();
        this.attachEventListeners();
    }

    /**
     * Start automatic status updates
     */
    startAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.updateInterval = setInterval(() => {
            this.updateServiceStatus();
        }, this.updateIntervalMs);
    }

    /**
     * Stop automatic status updates
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Update service status
     */
    updateServiceStatus() {
        fetch('/service-status')
            .then(response => response.json())
            .then(data => {
                const loading = document.getElementById('loading');
                const serviceStatus = document.getElementById('service-status');
                const serviceCard = document.getElementById('service-card');

                if (loading) loading.style.display = 'none';
                if (serviceStatus) serviceStatus.style.display = 'block';

                if (data.success) {
                    this.updateStatusDisplay(data, serviceCard);
                    this.lastUpdateTime = new Date();

                    const lastUpdatedEl = document.getElementById('last-updated');
                    if (lastUpdatedEl) {
                        lastUpdatedEl.textContent = `Last updated: ${this.lastUpdateTime.toLocaleTimeString()}`;
                    }
                } else {
                    this.handleStatusError(data, serviceCard);
                }
            })
            .catch(error => {
                console.error('Network error:', error);
                if (window.ui) {
                    window.ui.showToast('Failed to fetch service status', 'error');
                }
                const loading = document.getElementById('loading');
                if (loading) {
                    loading.textContent = 'Error loading service status';
                    loading.style.color = '#dc3545';
                }
            });
    }

    /**
     * Update status display elements
     */
    updateStatusDisplay(data, serviceCard) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');

        if (statusText) statusText.textContent = data.status;

        // Update card style and indicator based on status
        if (serviceCard) {
            serviceCard.className = 'service-card';
            if (data.active && data.status === 'active') {
                serviceCard.classList.add('active');
            } else if (data.status === 'inactive' || data.status === 'failed') {
                serviceCard.classList.add('inactive');
            }
        }

        if (statusIndicator) {
            statusIndicator.className = 'status-indicator';
            if (data.active && data.status === 'active') {
                statusIndicator.classList.add('status-active');
            } else if (data.status === 'inactive' || data.status === 'failed') {
                statusIndicator.classList.add('status-inactive');
            } else {
                statusIndicator.classList.add('status-unknown');
            }
        }

        // Update other status fields
        this.updateElementText('active-status', data.active ? 'Yes' : 'No');
        this.updateElementText('enabled-status', data.enabled ? 'Yes' : 'No');
        this.updateElementText('uptime', data.uptime || 'N/A');
        this.updateElementText('memory-usage', data.memory_usage || 'N/A');
        this.updateElementText('last-log', data.last_log || 'N/A');
    }

    /**
     * Handle status error
     */
    handleStatusError(data, serviceCard) {
        if (serviceCard) serviceCard.classList.add('inactive');
        this.updateElementText('status-text', 'Error');

        const statusIndicator = document.getElementById('status-indicator');
        if (statusIndicator) {
            statusIndicator.classList.add('status-inactive');
        }

        console.error('Error fetching service status:', data.error);
    }

    /**
     * Update element text content safely
     */
    updateElementText(id, text) {
        const element = document.getElementById(id);
        if (element) element.textContent = text;
    }

    /**
     * Control service (start/stop)
     */
    controlService(action) {
        const buttons = ['start-btn', 'stop-btn'];
        const actionBtn = document.getElementById(action + '-btn');

        if (!actionBtn) {
            console.error(`Button with ID ${action}-btn not found`);
            return;
        }

        // Disable all buttons during operation
        buttons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) btn.disabled = true;
        });

        // Show loading state
        const originalText = actionBtn.textContent;
        actionBtn.textContent = action.charAt(0).toUpperCase() + action.slice(1) + 'ing...';

        if (window.ui) {
            window.ui.showLoading(`${action.charAt(0).toUpperCase() + action.slice(1)}ing service...`);
        }

        fetch('/service-control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: action,
                service_name: 'jebi-switchboard-guard.service'
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (window.ui) window.ui.hideLoading();

            if (data.success) {
                if (window.ui) {
                    window.ui.showToast(
                        `Service ${action}ed successfully`,
                        'success'
                    );
                }
                // Refresh status after a short delay
                setTimeout(() => this.updateServiceStatus(), 1000);
            } else {
                if (window.ui) {
                    window.ui.showToast(
                        data.error || `Failed to ${action} service`,
                        'error'
                    );
                }
            }
        })
        .catch(error => {
            if (window.ui) window.ui.hideLoading();
            console.error('Error:', error);
            if (window.ui) {
                window.ui.showToast(
                    `Network error: ${error.message}`,
                    'error'
                );
            }
        })
        .finally(() => {
            // Re-enable buttons and restore text
            buttons.forEach(btnId => {
                const btn = document.getElementById(btnId);
                if (btn) btn.disabled = false;
            });
            actionBtn.textContent = originalText;
        });
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.controlService('start'));
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.controlService('stop'));
        }
    }
}

// Initialize global service monitor instance
window.serviceMonitor = new ServiceMonitor();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.serviceMonitor.init();
    });
} else {
    window.serviceMonitor.init();
}