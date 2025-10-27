# Light Schedule Cron Job Setup

## Overview
This cron job setup allows the light schedule to run automatically every minute, even when the browser is closed. The cron job calls the `/revpi-schedule/check` endpoint to enforce the schedule.

## Files Included

1. **`check_light_schedule.sh`** - Script that calls the API endpoint
2. **`install_cron.sh`** - Installs the cron job
3. **`uninstall_cron.sh`** - Removes the cron job

## Installation

### Step 1: Make scripts executable
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
chmod +x check_light_schedule.sh
chmod +x install_cron.sh
chmod +x uninstall_cron.sh
```

### Step 2: Run the installer
```bash
./install_cron.sh
```

The installer will:
- Make the check script executable
- Create log directory and file
- Add a cron job that runs every minute
- Display the installed cron job

### Step 3: Verify installation
```bash
# Check cron job is installed
crontab -l | grep check_light_schedule

# Watch the logs
tail -f /var/log/light-schedule-check.log
```

## How It Works

### Cron Schedule
```
* * * * * /path/to/check_light_schedule.sh
```
This means: Run every minute of every hour of every day

### What the Script Does
1. Calls `POST http://localhost:5000/revpi-schedule/check`
2. Receives response with action taken
3. Logs the result to `/var/log/light-schedule-check.log`
4. Rotates log file when it exceeds 10MB

### Log Format
```
2025-10-27 14:30:01 - Checking light schedule...
2025-10-27 14:30:01 - ACTION: turned_on - Light turned ON per schedule
2025-10-27 14:31:01 - Checking light schedule...
2025-10-27 14:31:01 - INFO: Light already ON (correct state)
```

## Testing

### Manual Test
Run the script manually to test:
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./check_light_schedule.sh
```

Check the output:
```bash
cat /var/log/light-schedule-check.log
```

### Verify Cron Execution
Wait 1-2 minutes after installation, then check logs:
```bash
tail -20 /var/log/light-schedule-check.log
```

You should see entries appearing every minute.

## Configuration

### Change API URL
Edit `check_light_schedule.sh` and modify:
```bash
API_URL="http://localhost:5000/revpi-schedule/check"
```

For example, if running on a different port:
```bash
API_URL="http://localhost:8080/revpi-schedule/check"
```

### Change Check Frequency

Edit cron job frequency:
```bash
crontab -e
```

Examples:
- Every 30 seconds: Use two cron entries (`:00` and `:30`)
- Every 2 minutes: `*/2 * * * *`
- Every 5 minutes: `*/5 * * * *`
- Every hour: `0 * * * *`

### Change Log Location
Edit `check_light_schedule.sh` and modify:
```bash
LOG_FILE="/var/log/light-schedule-check.log"
```

## Monitoring

### View Recent Logs
```bash
tail -50 /var/log/light-schedule-check.log
```

### Watch Live Logs
```bash
tail -f /var/log/light-schedule-check.log
```

### Check for Errors
```bash
grep ERROR /var/log/light-schedule-check.log
```

### Check Actions Taken
```bash
grep ACTION /var/log/light-schedule-check.log
```

### View Today's Activity
```bash
grep "$(date '+%Y-%m-%d')" /var/log/light-schedule-check.log
```

## Troubleshooting

### Cron Job Not Running

**Check if cron service is running:**
```bash
sudo systemctl status cron
```

**Start cron if stopped:**
```bash
sudo systemctl start cron
```

**View cron logs:**
```bash
sudo journalctl -u cron -f
```

### API Connection Errors

**Check if Flask app is running:**
```bash
ps aux | grep python | grep web.py
```

**Test API manually:**
```bash
curl -X POST http://localhost:5000/revpi-schedule/check
```

**Check if port is correct:**
```bash
netstat -tlnp | grep python
```

### Permission Errors

**Make script executable:**
```bash
chmod +x /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts/check_light_schedule.sh
```

**Fix log file permissions:**
```bash
sudo chown $USER:$USER /var/log/light-schedule-check.log
```

### Script Not Found

**Verify script location:**
```bash
ls -la /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts/check_light_schedule.sh
```

**Check cron job path:**
```bash
crontab -l | grep check_light_schedule
```

## Uninstallation

### Remove Cron Job
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./uninstall_cron.sh
```

Or manually:
```bash
crontab -e
# Delete the lines containing "check_light_schedule.sh"
```

### Remove Log Files
```bash
sudo rm /var/log/light-schedule-check.log*
```

## Integration with Flask App

### Prerequisites
- Flask app must be running on `http://localhost:5000`
- The `/revpi-schedule/check` endpoint must be accessible
- Light schedule must be configured and enabled in the app

### Auto-Start Flask App
To ensure Flask app starts on boot, create a systemd service or add to crontab:

```bash
# Add to crontab
@reboot cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring && python3 web.py
```

## Advantages of Cron Job vs Browser Polling

✅ **24/7 Operation** - Works even when browser is closed  
✅ **Server-Side** - No dependency on user's browser  
✅ **Reliable** - Cron is a standard Unix utility  
✅ **Resource Efficient** - Minimal CPU/memory usage  
✅ **Automatic** - Starts on system boot  
✅ **Logging** - Built-in logging for debugging  

## Example Schedule Behavior

### Scenario 1: Normal Operation
```
14:29 - Light is OFF (schedule: ON at 14:30)
14:30 - Cron runs, light turns ON
14:31 - Cron runs, light stays ON (correct state)
16:00 - Light is ON (schedule: OFF at 16:00)
16:00 - Cron runs, light turns OFF
```

### Scenario 2: Manual Override
```
14:35 - Light is ON (per schedule)
14:40 - User manually turns light OFF
14:41 - Cron runs, detects mismatch, turns light back ON
```

### Scenario 3: System Reboot
```
14:00 - System reboots
14:05 - Flask app starts
14:06 - Cron runs for first time, sets light to correct state
```

## Security Considerations

1. **Local Only**: Script calls localhost - no external network access
2. **No Authentication**: Endpoint doesn't require login (by design)
3. **Log Rotation**: Prevents disk space issues
4. **Error Handling**: Graceful failure on connection issues

## Best Practices

1. **Monitor Logs Daily**: Check for unexpected errors
2. **Test After Changes**: Run manual test after modifying schedule
3. **Keep Flask App Running**: Use systemd or supervisor
4. **Regular Backups**: Backup schedule database regularly
5. **Log Rotation**: Monitor log file size

## Support

For issues or questions:
1. Check logs: `/var/log/light-schedule-check.log`
2. Test manually: `./check_light_schedule.sh`
3. Verify Flask app is running
4. Check cron service status
5. Review endpoint response format

---

**Note**: This cron job is independent of the browser-based polling. You can use both simultaneously (harmless but redundant), or disable browser polling by commenting out the `setInterval(checkLightSchedule, 60000);` line in the frontend code.
