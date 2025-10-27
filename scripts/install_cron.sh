#!/bin/bash
#
# Installation script for Light Schedule Cron Job
# This sets up automatic light schedule checking every minute
#

set -e

echo "======================================"
echo "Light Schedule Cron Job Installer"
echo "======================================"
echo ""

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo "ERROR: crontab command not found!"
    echo ""
    echo "Your system doesn't have crontab installed."
    echo ""
    echo "Alternative options:"
    echo "1. Install cron:"
    echo "   sudo apt-get update && sudo apt-get install cron"
    echo ""
    echo "2. Use systemd timer instead (recommended):"
    echo "   sudo ./install_systemd_timer.sh"
    echo ""
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

# Create log directory if it doesn't exist
echo "Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/light-schedule-check.log
sudo chown $USER:$USER /var/log/light-schedule-check.log

# Check if cron job already exists
CRON_JOB="* * * * * $CHECK_SCRIPT >> /var/log/light-schedule-check.log 2>&1"
CRON_COMMENT="# JEBI Light Schedule Check - runs every minute"

echo "Checking for existing cron job..."
if crontab -l 2>/dev/null | grep -q "check_light_schedule.sh"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "check_light_schedule.sh" | grep -v "JEBI Light Schedule Check" | crontab -
fi

# Add the cron job
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo ""; echo "$CRON_COMMENT"; echo "$CRON_JOB") | crontab -

# Verify installation
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Cron job has been installed and will run every minute."
echo ""
echo "Current crontab:"
crontab -l | tail -3
echo ""
echo "To view logs:"
echo "  tail -f /var/log/light-schedule-check.log"
echo ""
echo "To test manually:"
echo "  $CHECK_SCRIPT"
echo ""
echo "To remove the cron job:"
echo "  crontab -e"
echo "  (then delete the lines with 'check_light_schedule.sh')"
echo ""
echo "Note: Make sure the Flask app is running on http://localhost:5000"
echo ""
