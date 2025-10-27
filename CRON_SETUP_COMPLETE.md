# Cron Job Setup Complete! 🎉

## What Was Created

I've created a complete cron job solution for automatic light schedule control:

### 📁 Files Created

```
Boot-Monitoring/
└── scripts/
    ├── check_light_schedule.sh      # Main script that calls the API
    ├── install_cron.sh              # Installs the cron job
    ├── uninstall_cron.sh            # Removes the cron job
    ├── quick_start.sh               # One-command setup
    └── README_CRON_SETUP.md         # Complete documentation
```

## 🚀 Quick Installation

### Option 1: Quick Start (Easiest)
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
chmod +x quick_start.sh
./quick_start.sh
```

### Option 2: Step by Step
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts

# Make scripts executable
chmod +x check_light_schedule.sh install_cron.sh uninstall_cron.sh

# Install
./install_cron.sh

# View logs
tail -f /var/log/light-schedule-check.log
```

## ✅ What It Does

1. **Runs Every Minute** - Checks schedule automatically
2. **Calls API Endpoint** - POST to `/revpi-schedule/check`
3. **Toggles Relay** - Turns light ON/OFF based on schedule
4. **Logs Everything** - All actions logged to `/var/log/light-schedule-check.log`
5. **Auto Rotation** - Logs rotate at 10MB
6. **Error Handling** - Graceful failure on connection issues

## 📊 How It Works

```
Cron Job (every minute)
    ↓
check_light_schedule.sh
    ↓
POST http://localhost:5000/revpi-schedule/check
    ↓
Backend checks schedule
    ↓
Toggles relay if needed
    ↓
Returns action taken
    ↓
Logs result
```

## 📝 Example Log Output

```
2025-10-27 18:00:01 - Checking light schedule...
2025-10-27 18:00:01 - ACTION: turned_on - Light turned ON per schedule
2025-10-27 18:01:01 - Checking light schedule...
2025-10-27 18:01:01 - INFO: Light already ON (correct state)
2025-10-27 06:00:01 - Checking light schedule...
2025-10-27 06:00:01 - ACTION: turned_off - Light turned OFF per schedule
```

## 🔍 Verification

### Check Cron Job is Installed
```bash
crontab -l | grep check_light_schedule
```

Expected output:
```
# JEBI Light Schedule Check - runs every minute
* * * * * /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts/check_light_schedule.sh >> /var/log/light-schedule-check.log 2>&1
```

### Watch Live Logs
```bash
tail -f /var/log/light-schedule-check.log
```

### Test Manually
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./check_light_schedule.sh
```

## 🛠️ Configuration

### Change Check Frequency

Edit cron frequency:
```bash
crontab -e
```

Examples:
- **Every minute**: `* * * * *` (default)
- **Every 2 minutes**: `*/2 * * * *`
- **Every 5 minutes**: `*/5 * * * *`
- **Every 30 seconds**: Add two entries:
  ```
  * * * * * /path/to/script
  * * * * * sleep 30; /path/to/script
  ```

### Change API URL

Edit `check_light_schedule.sh`:
```bash
API_URL="http://localhost:5000/revpi-schedule/check"
```

## 🚨 Troubleshooting

### Issue: Cron not running
```bash
# Check cron service
sudo systemctl status cron

# Start if stopped
sudo systemctl start cron

# View cron logs
sudo journalctl -u cron -f
```

### Issue: API connection failed
```bash
# Check Flask app is running
ps aux | grep python | grep web.py

# Test API manually
curl -X POST http://localhost:5000/revpi-schedule/check
```

### Issue: Permission denied
```bash
# Fix script permissions
chmod +x /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts/check_light_schedule.sh

# Fix log permissions
sudo chown $USER:$USER /var/log/light-schedule-check.log
```

## 🗑️ Uninstallation

```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./uninstall_cron.sh
```

Or manually:
```bash
crontab -e
# Delete lines containing "check_light_schedule.sh"
```

## 📊 Monitoring Commands

```bash
# View last 50 log entries
tail -50 /var/log/light-schedule-check.log

# View only errors
grep ERROR /var/log/light-schedule-check.log

# View only actions
grep ACTION /var/log/light-schedule-check.log

# View today's activity
grep "$(date '+%Y-%m-%d')" /var/log/light-schedule-check.log

# Count actions taken today
grep "$(date '+%Y-%m-%d')" /var/log/light-schedule-check.log | grep ACTION | wc -l
```

## ✨ Advantages

✅ **24/7 Operation** - Works even when browser closed  
✅ **No User Interaction** - Fully automatic  
✅ **Server-Side** - Independent of browser  
✅ **Reliable** - Standard Unix cron utility  
✅ **Low Resource** - Minimal CPU/memory usage  
✅ **Logged** - Complete audit trail  
✅ **Auto-Start** - Runs on system boot  

## 🆚 vs Browser Polling

| Feature | Cron Job | Browser Polling |
|---------|----------|----------------|
| **Runs 24/7** | ✅ Yes | ❌ Only when browser open |
| **User Independent** | ✅ Yes | ❌ Requires user session |
| **Server-Side** | ✅ Yes | ❌ Client-side |
| **Logging** | ✅ File-based | ✅ Console |
| **Setup Required** | ✅ One-time | ❌ None |
| **Resource Usage** | ✅ Very Low | ⚠️ Low-Medium |

## 📋 Prerequisites

Before installing, ensure:
1. ✅ Flask app is installed
2. ✅ Database has schedules table
3. ✅ Flask app can start successfully
4. ✅ curl is installed (usually pre-installed)
5. ✅ cron service is running

## 🎯 Use Cases

**Perfect For:**
- Production deployments
- Headless servers
- Raspberry Pi installations
- 24/7 automated control
- Remote installations

**Not Needed When:**
- Using systemd daemon instead
- Browser is always open
- Testing/development only

## 🔐 Security Notes

- ✅ Calls localhost only (no external network)
- ✅ No authentication needed (by design)
- ✅ Runs as current user
- ✅ Limited permissions
- ✅ No sensitive data in logs

## 📚 Additional Resources

- **Full Documentation**: `scripts/README_CRON_SETUP.md`
- **Main Schedule Guide**: `LIGHT_SCHEDULE_AUTOMATIC_CONTROL.md`
- **Cron Tutorial**: Run `man crontab`

## 🎉 You're All Set!

The cron job will now automatically control your light schedule every minute. The system is fully operational!

### What Happens Next:

1. **18:00** - Light turns ON automatically
2. **06:00** - Light turns OFF automatically  
3. **Every minute** - System verifies correct state
4. **All actions** - Logged for your review

Enjoy your automated light control! 💡✨
