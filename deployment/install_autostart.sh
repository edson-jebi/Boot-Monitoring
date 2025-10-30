#!/bin/bash
#
# Installation script for JEBI Web App Auto-Start on Boot
# This ensures Flask app and light schedule checker run automatically after reboot
#

set -e

echo "=========================================="
echo "JEBI Web App Auto-Start Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"
echo ""

# Step 1: Install Flask Web App Service
echo "Step 1: Installing Flask Web App Service..."
echo "-------------------------------------------"

# Copy service file
cp "$SCRIPT_DIR/jebi-web-app.service" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable jebi-web-app.service

# Start service now
systemctl start jebi-web-app.service

# Check status
if systemctl is-active --quiet jebi-web-app.service; then
    echo "✅ Flask Web App service started successfully"
else
    echo "⚠️  Flask Web App service may have issues, checking status..."
    systemctl status jebi-web-app.service --no-pager
fi

echo ""

# Step 2: Install Light Schedule Checker
echo "Step 2: Installing Light Schedule Checker..."
echo "----------------------------------------------"

cd "$PROJECT_DIR/scripts"

# Install systemd timer for schedule checking
if [ -f "./install_systemd_timer.sh" ]; then
    chmod +x ./install_systemd_timer.sh
    ./install_systemd_timer.sh
else
    echo "⚠️  install_systemd_timer.sh not found, skipping schedule checker"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Services installed and enabled:"
echo "  1. jebi-web-app.service        - Flask Web Application"
echo "  2. light-schedule-check.timer  - Light Schedule Automation"
echo ""
echo "These services will now start automatically on boot."
echo ""
echo "Useful commands:"
echo "  • Check Flask app status:     sudo systemctl status jebi-web-app"
echo "  • Check schedule timer:       sudo systemctl status light-schedule-check.timer"
echo "  • Restart Flask app:          sudo systemctl restart jebi-web-app"
echo "  • View Flask app logs:        sudo journalctl -u jebi-web-app -f"
echo "  • View schedule logs:         tail -f /var/log/light-schedule-check.log"
echo ""
echo "Web interface available at: http://$(hostname -I | awk '{print $1}'):5010"
echo ""
