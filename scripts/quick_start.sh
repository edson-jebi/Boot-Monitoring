#!/bin/bash
# Quick Start - Light Schedule Auto-Installer
# Automatically detects and uses the best installation method

echo "=========================================="
echo "Light Schedule Auto-Installer"
echo "=========================================="
echo ""

# Navigate to scripts directory
cd "$(dirname "$0")"

# Make all scripts executable
echo "Making scripts executable..."
chmod +x check_light_schedule.sh 
chmod +x install_cron.sh 
chmod +x uninstall_cron.sh
chmod +x install_systemd_timer.sh
chmod +x uninstall_systemd_timer.sh

echo ""
echo "Detecting best installation method..."
echo ""

# Check if systemd is available
if command -v systemctl &> /dev/null && systemctl --version &> /dev/null; then
    echo "✅ Systemd detected - Using systemd timer (recommended)"
    echo ""
    echo "Running installer..."
    sudo ./install_systemd_timer.sh
    
elif command -v crontab &> /dev/null; then
    echo "✅ Crontab detected - Using cron job"
    echo ""
    echo "Running installer..."
    ./install_cron.sh
    
else
    echo "❌ Neither systemd nor crontab found!"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "Option 1 - Install cron:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install cron"
    echo "  sudo systemctl enable cron"
    echo "  sudo systemctl start cron"
    echo ""
    echo "Option 2 - Your system should have systemd already"
    echo "  Try: sudo ./install_systemd_timer.sh"
    echo ""
    exit 1
fi

echo ""
echo "=========================================="
echo "Quick Start Complete!"
echo "=========================================="
echo ""
echo "The schedule checker is now running every minute."
echo ""
echo "Next steps:"
echo "1. Ensure Flask app is running: python3 web.py"
echo "2. Configure light schedule in the web interface"
echo "3. Enable the schedule toggle"
echo "4. Watch logs: tail -f /var/log/light-schedule-check.log"
echo ""
