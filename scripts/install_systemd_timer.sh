#!/bin/bash
#
# Installation script for Light Schedule using systemd timer (alternative to cron)
# This works on systems without crontab
#

set -e

echo "======================================"
echo "Light Schedule Systemd Timer Installer"
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
CHECK_SCRIPT="$PROJECT_DIR/scripts/check_light_schedule.sh"

echo "Project directory: $PROJECT_DIR"
echo "Check script: $CHECK_SCRIPT"
echo ""

# Check if check script exists
if [ ! -f "$CHECK_SCRIPT" ]; then
    echo "Error: check_light_schedule.sh not found at $CHECK_SCRIPT"
    exit 1
fi

# Make the check script executable
echo "Making check_light_schedule.sh executable..."
chmod +x "$CHECK_SCRIPT"

# Create log directory
echo "Creating log directory..."
mkdir -p /var/log
touch /var/log/light-schedule-check.log
chown $SUDO_USER:$SUDO_USER /var/log/light-schedule-check.log 2>/dev/null || true

# Create systemd service file
echo "Creating systemd service file..."
cat > /etc/systemd/system/light-schedule-check.service << EOF
[Unit]
Description=Light Schedule Check
After=network.target

[Service]
Type=oneshot
User=$SUDO_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$CHECK_SCRIPT
StandardOutput=append:/var/log/light-schedule-check.log
StandardError=append:/var/log/light-schedule-check.log

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer file
echo "Creating systemd timer file..."
cat > /etc/systemd/system/light-schedule-check.timer << EOF
[Unit]
Description=Light Schedule Check Timer
Requires=light-schedule-check.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start the timer
echo "Enabling and starting timer..."
systemctl enable light-schedule-check.timer
systemctl start light-schedule-check.timer

# Show status
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Timer status:"
systemctl status light-schedule-check.timer --no-pager
echo ""
echo "Next run time:"
systemctl list-timers light-schedule-check.timer --no-pager
echo ""
echo "To view logs:"
echo "  sudo journalctl -u light-schedule-check.service -f"
echo "  tail -f /var/log/light-schedule-check.log"
echo ""
echo "To check timer status:"
echo "  systemctl status light-schedule-check.timer"
echo ""
echo "To stop the timer:"
echo "  sudo systemctl stop light-schedule-check.timer"
echo ""
echo "To restart the timer:"
echo "  sudo systemctl restart light-schedule-check.timer"
echo ""
