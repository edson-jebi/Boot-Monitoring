#!/bin/bash
#
# Uninstallation script for JEBI Web App Auto-Start
# Removes all systemd services
#

set -e

echo "=========================================="
echo "JEBI Web App Auto-Start Uninstaller"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

echo "Stopping and disabling services..."
echo ""

# Stop and disable Flask Web App
if systemctl is-active --quiet jebi-web-app.service; then
    systemctl stop jebi-web-app.service
    echo "✅ Stopped jebi-web-app service"
fi

if systemctl is-enabled --quiet jebi-web-app.service; then
    systemctl disable jebi-web-app.service
    echo "✅ Disabled jebi-web-app service"
fi

# Remove service file
if [ -f "/etc/systemd/system/jebi-web-app.service" ]; then
    rm /etc/systemd/system/jebi-web-app.service
    echo "✅ Removed jebi-web-app.service file"
fi

# Stop and disable Light Schedule Timer
if systemctl is-active --quiet light-schedule-check.timer; then
    systemctl stop light-schedule-check.timer
    echo "✅ Stopped light-schedule-check.timer"
fi

if systemctl is-enabled --quiet light-schedule-check.timer; then
    systemctl disable light-schedule-check.timer
    echo "✅ Disabled light-schedule-check.timer"
fi

# Remove timer and service files
if [ -f "/etc/systemd/system/light-schedule-check.timer" ]; then
    rm /etc/systemd/system/light-schedule-check.timer
    echo "✅ Removed light-schedule-check.timer file"
fi

if [ -f "/etc/systemd/system/light-schedule-check.service" ]; then
    rm /etc/systemd/system/light-schedule-check.service
    echo "✅ Removed light-schedule-check.service file"
fi

# Reload systemd
systemctl daemon-reload

echo ""
echo "=========================================="
echo "Uninstallation Complete!"
echo "=========================================="
echo ""
echo "All auto-start services have been removed."
echo "The Flask app and schedule checker will no longer start on boot."
echo ""
