# Simple Install Script Update - Summary

## Changes Made

The `deployment/simple_install.sh` script has been updated to include automatic installation of the Light Schedule Checker service.

## What Was Added

### 1. Light Schedule Service Installation (Lines ~145-220)

After the main Flask application is installed and verified, the script now:

1. **Locates the check script**
   - Looks for `/home/pi/Boot-Monitoring/scripts/check_light_schedule.sh`
   - Makes it executable

2. **Creates log infrastructure**
   - Creates `/var/log/light-schedule-check.log`
   - Sets proper ownership for the `pi` user

3. **Installs systemd service**
   - Creates `/etc/systemd/system/light-schedule-check.service`
   - Configures it as a oneshot service
   - Depends on the main `boot-monitoring.service`
   - Logs to `/var/log/light-schedule-check.log`

4. **Installs systemd timer**
   - Creates `/etc/systemd/system/light-schedule-check.timer`
   - Runs every 1 minute (OnUnitActiveSec=1min)
   - Starts 1 minute after boot (OnBootSec=1min)
   - High accuracy (AccuracySec=1s)

5. **Enables and starts the timer**
   - Reloads systemd daemon
   - Enables timer for auto-start on boot
   - Starts timer immediately
   - Verifies successful start

### 2. Updated Installation Summary (Lines ~240-286)

Enhanced the final output to include:

- ⏰ **Light Schedule Management section**
  - Timer status command
  - Log viewing commands
  - Timer management commands
  - Start/stop instructions

- 📁 **Additional file locations**
  - Schedule service file location
  - Schedule timer file location
  - Schedule log file location

## Services Now Installed

### Main Application
- **Service:** `boot-monitoring.service`
- **Port:** 5000
- **Workers:** 2 Gunicorn workers
- **Auto-start:** Enabled on boot

### Light Schedule Checker
- **Service:** `light-schedule-check.service` (oneshot)
- **Timer:** `light-schedule-check.timer`
- **Frequency:** Every 1 minute
- **Log:** `/var/log/light-schedule-check.log`
- **Auto-start:** Enabled on boot

## Installation Command

```bash
cd /home/pi/Boot-Monitoring/deployment
sudo ./simple_install.sh
```

## Post-Installation Verification

### Check Main Application
```bash
sudo systemctl status boot-monitoring
curl http://localhost:5000
```

### Check Light Schedule Timer
```bash
sudo systemctl status light-schedule-check.timer
sudo systemctl list-timers light-schedule-check.timer
tail -f /var/log/light-schedule-check.log
```

### View All Services
```bash
systemctl list-units | grep -E "(boot-monitoring|light-schedule-check)"
```

## Key Features

✅ **Automatic Installation** - Single command installs everything  
✅ **Production Ready** - Gunicorn with proper configuration  
✅ **Auto-start on Boot** - Both services start automatically  
✅ **Independent Operation** - Schedule works without browser  
✅ **Proper Logging** - Separate logs for troubleshooting  
✅ **Systemd Integration** - Native Linux service management  
✅ **Firewall Configuration** - Automatic port opening  
✅ **Error Handling** - Validates each step  

## Rollback/Uninstall

Use the existing uninstall script:
```bash
sudo /home/pi/Boot-Monitoring/deployment/uninstall_autostart.sh
```

Or manual removal:
```bash
sudo systemctl stop boot-monitoring light-schedule-check.timer
sudo systemctl disable boot-monitoring light-schedule-check.timer
sudo rm /etc/systemd/system/boot-monitoring.service
sudo rm /etc/systemd/system/light-schedule-check.*
sudo systemctl daemon-reload
```

## Testing the Installation

### 1. Install
```bash
cd /home/pi/Boot-Monitoring/deployment
sudo ./simple_install.sh
```

### 2. Verify Services Running
```bash
systemctl is-active boot-monitoring
systemctl is-active light-schedule-check.timer
```

### 3. Test Web Interface
```bash
# Open browser to http://[PI_IP]:5000
# Or test with curl
curl http://localhost:5000
```

### 4. Configure Schedule
- Navigate to Settings → Light Schedule Configuration
- Set ON time (e.g., 18:00) and OFF time (e.g., 06:00)
- Save changes
- Enable schedule on Dashboard

### 5. Monitor Schedule Execution
```bash
tail -f /var/log/light-schedule-check.log
```

### 6. Test Reboot Persistence
```bash
sudo reboot
# After reboot, check services
systemctl status boot-monitoring
systemctl status light-schedule-check.timer
```

## Architecture

```
Boot-Monitoring Application
├── boot-monitoring.service (Main Flask App)
│   ├── Gunicorn WSGI Server
│   ├── Port: 5000
│   ├── Workers: 2
│   └── Auto-restart: Enabled
│
└── light-schedule-check.timer (Schedule Automation)
    ├── Frequency: Every 1 minute
    ├── Executes: light-schedule-check.service
    ├── Logs: /var/log/light-schedule-check.log
    └── Auto-start: Enabled on boot
```

## Dependencies

The Light Schedule Checker depends on:
- Main Flask application running (after dependency)
- `scripts/check_light_schedule.sh` script
- `scripts/config.sh` for port configuration
- Flask API endpoint: `/revpi-schedule/check`
- Database: `dev_users.db` with schedules table

## Files Modified

1. **deployment/simple_install.sh**
   - Added light schedule service installation (83 lines)
   - Updated final summary output
   - Enhanced documentation

2. **SIMPLE_INSTALL_GUIDE.md** (NEW)
   - Comprehensive installation guide
   - Service management instructions
   - Troubleshooting section
   - Configuration examples

3. **SIMPLE_INSTALL_UPDATE_SUMMARY.md** (THIS FILE)
   - Summary of changes
   - Testing procedures
   - Architecture documentation

## Next Steps

1. Test the updated installer on a clean system
2. Verify both services start correctly
3. Test schedule functionality
4. Verify persistence across reboots
5. Update main README.md with new installation method
6. Create video/screenshot tutorial

---

**Updated:** October 27, 2025  
**Version:** 2.0  
**Author:** Boot-Monitoring Team
