# Light Schedule Automatic Installation Guide

## Quick Start - Choose Your Method

Your system may use either **cron** or **systemd** for scheduling. Here's how to install:

---

## Method 1: Systemd Timer (Recommended)

**Best for:** Modern Linux systems, Raspberry Pi OS, Ubuntu 16.04+

### Installation
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
chmod +x install_systemd_timer.sh
sudo ./install_systemd_timer.sh
```

### Verification
```bash
# Check timer status
systemctl status light-schedule-check.timer

# Check when next run is scheduled
systemctl list-timers light-schedule-check.timer

# View logs
sudo journalctl -u light-schedule-check.service -f
# OR
tail -f /var/log/light-schedule-check.log
```

### Uninstallation
```bash
sudo ./uninstall_systemd_timer.sh
```

---

## Method 2: Cron Job (Alternative)

**Best for:** Older systems, systems with cron already installed

### Check if cron is available
```bash
which crontab
```

If command not found, install cron:
```bash
sudo apt-get update
sudo apt-get install cron
sudo systemctl enable cron
sudo systemctl start cron
```

### Installation
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
chmod +x install_cron.sh
./install_cron.sh
```

### Verification
```bash
# Check cron job
crontab -l | grep check_light_schedule

# View logs
tail -f /var/log/light-schedule-check.log
```

### Uninstallation
```bash
./uninstall_cron.sh
```

---

## Comparison: Systemd vs Cron

| Feature | Systemd Timer | Cron Job |
|---------|---------------|----------|
| **Setup** | `sudo` required | No `sudo` needed |
| **Logging** | journalctl + file | File only |
| **Status Check** | `systemctl status` | Check crontab |
| **Modern** | ✅ Yes | ⚠️ Legacy |
| **Persistent** | ✅ Yes | ✅ Yes |
| **Accuracy** | ✅ 1 second | ⚠️ 1 minute |

---

## Troubleshooting

### Issue: "crontab: command not found"

**Solution:** Your system doesn't have cron. Use systemd timer instead:
```bash
sudo ./install_systemd_timer.sh
```

Or install cron:
```bash
sudo apt-get install cron
```

### Issue: "Failed to start timer"

**Solution:** Check systemd logs:
```bash
sudo journalctl -xe
sudo systemctl status light-schedule-check.timer
```

### Issue: Script not executing

**Check 1:** Is Flask app running?
```bash
ps aux | grep python | grep web.py
```

**Check 2:** Test script manually:
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./check_light_schedule.sh
```

**Check 3:** Check permissions:
```bash
ls -la check_light_schedule.sh
# Should show: -rwxr-xr-x
```

### Issue: "Permission denied" on log file

**Solution:** Fix log file permissions:
```bash
sudo touch /var/log/light-schedule-check.log
sudo chown $USER:$USER /var/log/light-schedule-check.log
```

---

## Testing

### Test the script manually
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
./check_light_schedule.sh
```

Expected output in log:
```
2025-10-27 14:30:01 - Checking light schedule...
2025-10-27 14:30:01 - INFO: Light already ON (correct state)
```

### Watch for automatic execution

**For Systemd:**
```bash
# Watch in real-time
sudo journalctl -u light-schedule-check.service -f
```

**For Cron:**
```bash
# Watch log file
tail -f /var/log/light-schedule-check.log
```

Wait 1-2 minutes and you should see new entries appearing.

---

## Common Commands

### Systemd Timer Commands
```bash
# Check status
systemctl status light-schedule-check.timer

# View next run time
systemctl list-timers light-schedule-check.timer

# View service logs
sudo journalctl -u light-schedule-check.service -f

# Stop timer
sudo systemctl stop light-schedule-check.timer

# Start timer
sudo systemctl start light-schedule-check.timer

# Restart timer
sudo systemctl restart light-schedule-check.timer

# Disable (prevent auto-start on boot)
sudo systemctl disable light-schedule-check.timer

# Enable (auto-start on boot)
sudo systemctl enable light-schedule-check.timer
```

### Cron Commands
```bash
# View cron jobs
crontab -l

# Edit cron jobs
crontab -e

# View cron logs (if available)
grep CRON /var/log/syslog
```

---

## Which Method Should I Use?

### Use **Systemd Timer** if:
- ✅ You're on Raspberry Pi OS
- ✅ You're on Ubuntu 16.04 or newer
- ✅ You're on Debian 8 or newer
- ✅ You want better logging
- ✅ You want more control

### Use **Cron** if:
- ✅ You're on older Linux
- ✅ You already use cron for other tasks
- ✅ You prefer traditional methods
- ✅ You don't have sudo access

### Not sure? Try this:
```bash
# Check if systemd is available
systemctl --version

# If you see version info, use systemd timer
# If command not found, use cron
```

---

## Next Steps After Installation

1. **Start Flask app** (if not already running):
   ```bash
   cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring
   python3 web.py
   ```

2. **Configure schedule** in web interface:
   - Go to Settings → Light Schedule Configuration
   - Set ON time and OFF time
   - Select days
   - Save changes

3. **Enable schedule**:
   - Toggle "Light Schedule" to ON
   - Verify light turns on/off immediately

4. **Monitor logs**:
   ```bash
   tail -f /var/log/light-schedule-check.log
   ```

5. **Wait and verify**:
   - Wait 1-2 minutes
   - Check logs show automatic checks
   - Verify light toggles at scheduled times

---

## Support

If you encounter issues:

1. Check logs: `/var/log/light-schedule-check.log`
2. Test script manually: `./check_light_schedule.sh`
3. Verify Flask app is running: `ps aux | grep web.py`
4. Check schedule in database
5. Review systemd/cron status

---

**Tip:** Both methods work equally well. Systemd timer is more modern and recommended for most users.
