#!/bin/bash
# Installation script for JEBI Light Schedule Daemon

set -e

echo "======================================"
echo "JEBI Light Schedule Daemon Installer"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Check if schedule_daemon.py exists
if [ ! -f "$PROJECT_DIR/schedule_daemon.py" ]; then
    echo "Error: schedule_daemon.py not found at $PROJECT_DIR/schedule_daemon.py"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SCRIPT_DIR/jebi-schedule-daemon.service" ]; then
    echo "Error: jebi-schedule-daemon.service not found at $SCRIPT_DIR/jebi-schedule-daemon.service"
    exit 1
fi

# Make schedule_daemon.py executable
echo "Making schedule_daemon.py executable..."
chmod +x "$PROJECT_DIR/schedule_daemon.py"

# Copy service file to systemd directory
echo "Installing systemd service..."
cp "$SCRIPT_DIR/jebi-schedule-daemon.service" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling jebi-schedule-daemon service..."
systemctl enable jebi-schedule-daemon.service

# Start the service
echo "Starting jebi-schedule-daemon service..."
systemctl start jebi-schedule-daemon.service

# Check status
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Service status:"
systemctl status jebi-schedule-daemon.service --no-pager
echo ""
echo "To view logs:"
echo "  sudo journalctl -u jebi-schedule-daemon.service -f"
echo ""
echo "To check log file:"
echo "  sudo tail -f /var/log/jebi-schedule-daemon.log"
echo ""
echo "To stop the service:"
echo "  sudo systemctl stop jebi-schedule-daemon.service"
echo ""
echo "To restart the service:"
echo "  sudo systemctl restart jebi-schedule-daemon.service"
echo ""
