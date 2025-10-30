#!/bin/bash
#
# Uninstallation script for Light Schedule Cron Job
#

echo "======================================"
echo "Light Schedule Cron Job Uninstaller"
echo "======================================"
echo ""

# Check if cron job exists
if crontab -l 2>/dev/null | grep -q "check_light_schedule.sh"; then
    echo "Found existing cron job. Removing..."
    crontab -l 2>/dev/null | grep -v "check_light_schedule.sh" | grep -v "JEBI Light Schedule Check" | crontab -
    echo "Cron job removed successfully."
else
    echo "No cron job found."
fi

echo ""
echo "Current crontab:"
crontab -l 2>/dev/null || echo "(empty)"
echo ""
echo "Note: Log file at /var/log/light-schedule-check.log was not deleted."
echo "To remove it manually:"
echo "  sudo rm /var/log/light-schedule-check.log*"
echo ""
