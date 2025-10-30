#!/bin/bash
#
# Uninstallation script for Light Schedule systemd timer
#

echo "======================================"
echo "Light Schedule Timer Uninstaller"
echo "======================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Stop and disable timer
echo "Stopping and disabling timer..."
systemctl stop light-schedule-check.timer 2>/dev/null || true
systemctl disable light-schedule-check.timer 2>/dev/null || true

# Remove systemd files
echo "Removing systemd files..."
rm -f /etc/systemd/system/light-schedule-check.service
rm -f /etc/systemd/system/light-schedule-check.timer

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload
systemctl reset-failed

echo ""
echo "======================================"
echo "Uninstallation Complete!"
echo "======================================"
echo ""
echo "Timer has been removed."
echo ""
echo "Note: Log file at /var/log/light-schedule-check.log was not deleted."
echo "To remove it manually:"
echo "  sudo rm /var/log/light-schedule-check.log*"
echo ""
