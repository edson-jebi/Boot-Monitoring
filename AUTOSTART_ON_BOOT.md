# Auto-Start on Boot Setup

This guide shows you how to make the JEBI Web Application and Light Schedule system start automatically when the RevPi reboots.

## 🚀 Quick Installation

Run this **one command** to install everything:

```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/deployment
sudo ./install_autostart.sh
```

This installs:
1. **Flask Web App Service** - Starts web interface on boot (port 5010)
2. **Light Schedule Timer** - Checks schedule every minute automatically

---

## ✅ What Gets Installed

### 1. Flask Web App Service (`jebi-web-app.service`)

**What it does:**
- Starts Flask web application automatically on boot
- Restarts automatically if it crashes
- Runs in background (doesn't need terminal open)

**Service Details:**
- **Service File:** `/etc/systemd/system/jebi-web-app.service`
- **User:** `pi`
- **Port:** `5010`
- **Auto-restart:** Yes (10 second delay)
- **Logs:** `sudo journalctl -u jebi-web-app -f`

### 2. Light Schedule Checker (`light-schedule-check.timer`)

**What it does:**
- Checks light schedule every minute
- Turns lights ON/OFF at scheduled times
- Works even when browser is closed
- Runs independently of web interface

**Service Details:**
- **Timer File:** `/etc/systemd/system/light-schedule-check.timer`
- **Service File:** `/etc/systemd/system/light-schedule-check.service`
- **Frequency:** Every 1 minute
- **Script:** `/home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts/check_light_schedule.sh`
- **Logs:** `/var/log/light-schedule-check.log`

---

## 📋 Management Commands

### Check Status

```bash
# Check Flask web app status
sudo systemctl status jebi-web-app

# Check schedule timer status
sudo systemctl status light-schedule-check.timer

# Check if services are enabled on boot
systemctl is-enabled jebi-web-app
systemctl is-enabled light-schedule-check.timer
```

### Start/Stop Services

```bash
# Start Flask app
sudo systemctl start jebi-web-app

# Stop Flask app
sudo systemctl stop jebi-web-app

# Restart Flask app (after code changes)
sudo systemctl restart jebi-web-app

# Start schedule timer
sudo systemctl start light-schedule-check.timer

# Stop schedule timer
sudo systemctl stop light-schedule-check.timer
```

### View Logs

```bash
# Flask app logs (real-time)
sudo journalctl -u jebi-web-app -f

# Flask app logs (last 50 lines)
sudo journalctl -u jebi-web-app -n 50

# Schedule check logs
tail -f /var/log/light-schedule-check.log

# Schedule check logs (last 20 lines)
tail -20 /var/log/light-schedule-check.log
```

### Disable Auto-Start

```bash
# Disable Flask app from starting on boot (but don't remove it)
sudo systemctl disable jebi-web-app

# Disable schedule checker from starting on boot
sudo systemctl disable light-schedule-check.timer

# To enable again
sudo systemctl enable jebi-web-app
sudo systemctl enable light-schedule-check.timer
```

### Complete Removal

```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/deployment
sudo ./uninstall_autostart.sh
```

---

## 🧪 Testing

### Test Auto-Start After Installation

```bash
# Check services are running
sudo systemctl status jebi-web-app
sudo systemctl status light-schedule-check.timer

# Access web interface
curl http://localhost:5010

# Check if schedule endpoint works
curl -X POST http://localhost:5010/revpi-schedule/check
```

### Test Auto-Start After Reboot

```bash
# Reboot the system
sudo reboot

# Wait for system to come back online, then SSH in and check:
sudo systemctl status jebi-web-app
sudo systemctl status light-schedule-check.timer

# Both should show "active (running)"
```

---

## 🔧 Troubleshooting

### Issue: Flask app fails to start

**Check logs:**
```bash
sudo journalctl -u jebi-web-app -n 100
```

**Common causes:**
1. **Virtual environment issue**: Service file uses hardcoded venv path
   - Check: `/home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/venv/bin/python3`
2. **Missing dependencies**: `pip install -r requirements.txt` in venv
3. **Port already in use**: Another process using port 5010
   - Check: `netstat -tulpn | grep 5010`

**Fix:**
```bash
# Restart the service
sudo systemctl restart jebi-web-app

# Check status
sudo systemctl status jebi-web-app
```

### Issue: Schedule checker not running

**Check timer status:**
```bash
systemctl status light-schedule-check.timer
systemctl list-timers light-schedule-check.timer
```

**Check logs:**
```bash
tail -50 /var/log/light-schedule-check.log
```

**Common causes:**
1. **Flask app not running**: Schedule checker needs Flask API
2. **Wrong port**: Check `scripts/config.sh` has correct FLASK_PORT
3. **Script permissions**: Check `check_light_schedule.sh` is executable

**Fix:**
```bash
# Restart timer
sudo systemctl restart light-schedule-check.timer

# Check logs
tail -f /var/log/light-schedule-check.log
```

### Issue: Services don't start on boot

**Verify services are enabled:**
```bash
systemctl is-enabled jebi-web-app
systemctl is-enabled light-schedule-check.timer
```

**If not enabled:**
```bash
sudo systemctl enable jebi-web-app
sudo systemctl enable light-schedule-check.timer
```

**Check boot logs:**
```bash
sudo journalctl -b | grep jebi
```

---

## 📊 Monitoring

### Dashboard to Check Everything Works

```bash
# Create a simple monitoring script
cat > ~/check_jebi_status.sh << 'EOF'
#!/bin/bash
echo "========================================"
echo "JEBI System Status"
echo "========================================"
echo ""

echo "Flask Web App:"
systemctl is-active jebi-web-app && echo "  ✅ Running" || echo "  ❌ Not running"
echo ""

echo "Schedule Timer:"
systemctl is-active light-schedule-check.timer && echo "  ✅ Running" || echo "  ❌ Not running"
echo ""

echo "Next schedule check:"
systemctl list-timers light-schedule-check.timer --no-pager | grep light-schedule
echo ""

echo "Recent schedule log:"
tail -5 /var/log/light-schedule-check.log
echo ""

echo "Web interface:"
curl -s http://localhost:5010 > /dev/null && echo "  ✅ Accessible" || echo "  ❌ Not accessible"
echo ""
EOF

chmod +x ~/check_jebi_status.sh

# Run it
~/check_jebi_status.sh
```

---

## 🎯 Benefits of Auto-Start

✅ **Survives Reboots** - System comes back online automatically  
✅ **No Manual Intervention** - Everything starts without user action  
✅ **Browser Independent** - Works even when no one is logged in  
✅ **Automatic Recovery** - Services restart if they crash  
✅ **Production Ready** - Suitable for deployed systems  
✅ **Easy Management** - Standard systemd commands  

---

## 📁 Service Files Location

```
/etc/systemd/system/
├── jebi-web-app.service              # Flask web app
├── light-schedule-check.service      # Schedule checker (oneshot)
└── light-schedule-check.timer        # Timer trigger (every 1 min)
```

---

## 🔄 After Code Changes

When you update the code:

```bash
# If you changed Python code:
sudo systemctl restart jebi-web-app

# If you changed check_light_schedule.sh:
sudo systemctl restart light-schedule-check.timer

# If you changed config.sh:
# No restart needed, will be picked up on next check
```

---

## Summary

**Installation:**
```bash
sudo ./deployment/install_autostart.sh
```

**Verification:**
```bash
sudo systemctl status jebi-web-app
sudo systemctl status light-schedule-check.timer
```

**Removal:**
```bash
sudo ./deployment/uninstall_autostart.sh
```

That's it! Your system will now automatically start on every reboot. 🎉
