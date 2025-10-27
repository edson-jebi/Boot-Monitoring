#!/bin/bash
#
# Test Light Schedule System
# This script verifies that the automatic light schedule is working correctly
#

echo "==========================================="
echo "Light Schedule System - Test Script"
echo "==========================================="
echo ""

# Check if Flask is running
echo "1. Checking if Flask app is running..."
if pgrep -f "python.*web.py" > /dev/null; then
    echo "   ✅ Flask app is running"
    FLASK_PID=$(pgrep -f "python.*web.py" | head -1)
    echo "   PID: $FLASK_PID"
else
    echo "   ❌ Flask app is NOT running!"
    echo "   Start it with: cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring && source venv/bin/activate && python3 web.py"
    exit 1
fi

echo ""
echo "2. Testing schedule check endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:5010/revpi-schedule/check)
if echo "$RESPONSE" | grep -q "success"; then
    echo "   ✅ Endpoint is working"
    echo "   Response: $RESPONSE"
else
    echo "   ❌ Endpoint failed"
    echo "   Response: $RESPONSE"
    exit 1
fi

echo ""
echo "3. Checking current schedule..."
SCHEDULE=$(curl -s http://localhost:5010/revpi-schedule/get/RelayLight)
if echo "$SCHEDULE" | grep -q "success"; then
    echo "   ✅ Schedule retrieved"
    echo "$SCHEDULE" | python3 -m json.tool 2>/dev/null || echo "$SCHEDULE"
else
    echo "   ⚠️  No schedule configured yet"
    echo "   Configure it in the web UI: Settings → Light Schedule"
fi

echo ""
echo "4. Checking scheduler installation..."
if systemctl list-timers --all 2>/dev/null | grep -q "light-schedule-check"; then
    echo "   ✅ Systemd timer is installed"
    systemctl status light-schedule-check.timer --no-pager | head -5
elif crontab -l 2>/dev/null | grep -q "check_light_schedule"; then
    echo "   ✅ Cron job is installed"
    crontab -l | grep check_light_schedule
else
    echo "   ⚠️  No scheduler installed"
    echo "   Install with: cd scripts && sudo ./quick_start.sh"
fi

echo ""
echo "5. Checking logs..."
if [ -f /var/log/light-schedule-check.log ]; then
    echo "   ✅ Log file exists"
    echo "   Last 3 entries:"
    tail -3 /var/log/light-schedule-check.log
else
    echo "   ⚠️  No log file yet (will be created when scheduler runs)"
fi

echo ""
echo "==========================================="
echo "Test Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Configure schedule in web UI if not done yet"
echo "2. Install scheduler if not installed: cd scripts && sudo ./quick_start.sh"
echo "3. Monitor logs: tail -f /var/log/light-schedule-check.log"
echo ""
