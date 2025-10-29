# Boot-Monitoring - Quick Installation Guide

## For New RevPi Devices

This guide will help you install Boot-Monitoring (Bradken SwitchOS) on a fresh Revolution Pi device.

---

## 📋 Prerequisites

- Revolution Pi device
- Network/Internet connection
- SSH or terminal access
- 5-10 minutes

---

## 🚀 Installation (3 Steps)

### Step 1: Get the Code on Your RevPi

Choose the method that works for you:

**Option A - Using Git (Easiest):**
```bash
cd /home/pi
git clone <repository-url> Boot-Monitoring
```

**Option B - Copy via SCP from your computer:**
```bash
scp -r /path/to/Boot-Monitoring pi@<revpi-ip>:/home/pi/
```

**Option C - Using USB Drive:**
```bash
# Insert USB drive, then:
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb
cp -r /mnt/usb/Boot-Monitoring /home/pi/
sudo umount /mnt/usb
```

### Step 2: Run the Installer

```bash
cd /home/pi/Boot-Monitoring/deployment
sudo ./simple_install.sh
```

⏱️ Installation takes about 3-5 minutes depending on internet speed.

### Step 3: Access the Application

After installation completes, you'll see the access URL. Open it in your browser:

```
http://<revpi-ip-address>:5000
```

**Default Login:**
- Username: `bradken`
- Password: `adminBradken25`

🔒 **Important:** Change the password after first login!

---

## ✅ What Gets Installed

The installer automatically sets up:

- ✓ Python 3 virtual environment
- ✓ Flask web application
- ✓ Gunicorn production server
- ✓ SQLite database
- ✓ Systemd services (auto-start on boot)
- ✓ Light schedule automation
- ✓ Firewall configuration
- ✓ Secure environment configuration

---

## 🎯 First-Time Setup Checklist

After logging in, complete these steps:

1. **Change Password** (Settings → User Management)
2. **Configure System Information** (Settings → System Information)
   - System Code
   - Equipment/Site name
   - Location Code
3. **Set Timezone** (Settings → Timezone)
4. **Configure Network** (Settings → Network Configuration)
   - Screen IP address
   - Processor IP address
5. **Configure Auto Power Cycle** (Dashboard → Auto Power Cycle)
   - Set monitoring interval
   - Set retry attempts
   - Set cooldown period
6. **Optional: Set Light Schedule** (Dashboard → Lights)

---

## 🔧 Common Commands

### Service Management
```bash
# Check service status
systemctl status boot-monitoring

# View live logs
journalctl -fu boot-monitoring

# Restart application
sudo systemctl restart boot-monitoring
```

### Accessing Logs
```bash
# Application logs
journalctl -u boot-monitoring -n 100

# Light schedule logs
tail -f /var/log/light-schedule-check.log
```

---

## 🔥 Troubleshooting

### Can't Access the Application?

1. **Check if service is running:**
```bash
systemctl status boot-monitoring
```

2. **Check the IP address:**
```bash
hostname -I
```

3. **Check firewall:**
```bash
sudo firewall-cmd --list-all
```

### Service Failed to Start?

View error logs:
```bash
journalctl -u boot-monitoring -n 50 --no-pager
```

### Need to Reinstall?

```bash
cd /home/pi/Boot-Monitoring/deployment
sudo ./simple_install.sh
```

The script is safe to run multiple times.

---

## 📱 Features Overview

### Dashboard
- **Real-time device status monitoring**
- **Power Cycle Events timeline** (auto-refreshes every 10s)
- **Manual relay controls** (Screen, Processor, Lights)
- **Auto Power Cycle configuration**
- **Light schedule setup**

### Settings
- **System Information** (persisted across reboots)
- **Network Configuration** (device IP addresses)
- **Auto Power Cycle** (monitoring intervals, retries)
- **Light Schedule** (automatic ON/OFF times)
- **Timezone configuration** (with NTP sync)

### System Logs
- **Jebi-Switchboard activity logs**
- **Date range filtering**
- **Download logs as text file**
- **Real-time updates**

---

## 🌐 Network Requirements

The application communicates with:
- **Screen device** (configured IP)
- **Processor device** (configured IP)
- **NTP servers** (for time sync)
- **Internet** (optional, for updates)

Default port: **5000**

---

## 📚 Additional Resources

- **Full Documentation:** `deployment/README.md`
- **Installation Script:** `deployment/simple_install.sh`
- **Application Code:** `app/` directory
- **Configuration:** `.env` file

---

## 🆘 Need Help?

1. Check service logs: `journalctl -u boot-monitoring -n 100`
2. Check service status: `systemctl status boot-monitoring`
3. Review the full README: `deployment/README.md`
4. Check application logs in web interface (Logs page)

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| **View status** | `systemctl status boot-monitoring` |
| **View logs** | `journalctl -fu boot-monitoring` |
| **Restart app** | `sudo systemctl restart boot-monitoring` |
| **Stop app** | `sudo systemctl stop boot-monitoring` |
| **Start app** | `sudo systemctl start boot-monitoring` |
| **Check IP** | `hostname -I` |
| **Check port** | `sudo netstat -tulpn \| grep 5000` |

---

## 🎉 You're All Set!

Your Boot-Monitoring application is now installed and running. Access it at:

**http://your-revpi-ip:5000**

Enjoy monitoring and controlling your RevPi devices! 🚀
