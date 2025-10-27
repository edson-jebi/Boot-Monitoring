# Simple Installation Guide

## Overview

The `simple_install.sh` script provides a complete, production-ready installation of the Boot-Monitoring application with the following features:

- ✅ Flask Web Application with Gunicorn WSGI server
- ✅ Virtual environment setup
- ✅ Systemd service for auto-start on boot
- ✅ Light Schedule Automation (systemd timer)
- ✅ Secure environment configuration
- ✅ Firewall configuration
- ✅ Automatic log management

## Prerequisites

- Debian/Ubuntu-based Linux system (Raspberry Pi OS recommended)
- Root access (sudo privileges)
- Python 3.7 or higher
- Internet connection for package installation

## Installation

### One-Command Installation

```bash
sudo /home/pi/Boot-Monitoring/deployment/simple_install.sh
```

Or navigate to the deployment directory first:

```bash
cd /home/pi/Boot-Monitoring/deployment
sudo ./simple_install.sh
```

### What Gets Installed

1. **System Dependencies**
   - Python 3
   - Python 3 pip
   - Python 3 venv

2. **Python Environment**
   - Virtual environment at `/home/pi/Boot-Monitoring/venv`
   - All dependencies from `requirements.txt`
   - Gunicorn WSGI server
   - Python-dotenv for environment management

3. **Application Configuration**
   - Production environment file (`.env`)
   - Secure random SECRET_KEY
   - WSGI entry point (`wsgi.py`)
   - Gunicorn configuration (`gunicorn.conf.py`)

4. **Systemd Services**
   - `boot-monitoring.service` - Main Flask application
   - `light-schedule-check.service` - Light schedule checker (oneshot)
   - `light-schedule-check.timer` - Timer to run schedule checks every minute

5. **Firewall Configuration**
   - Port 5000 opened for web access
   - Works with firewalld or ufw

## Services Installed

### 1. Boot-Monitoring Service (Main Application)

**Service Name:** `boot-monitoring.service`

**Features:**
- Runs Flask app with Gunicorn
- 2 worker processes
- Auto-restart on failure
- Starts automatically on boot

**Management Commands:**
```bash
# Check status
sudo systemctl status boot-monitoring

# View logs (follow mode)
sudo journalctl -fu boot-monitoring

# Start service
sudo systemctl start boot-monitoring

# Stop service
sudo systemctl stop boot-monitoring

# Restart service
sudo systemctl restart boot-monitoring

# Disable auto-start
sudo systemctl disable boot-monitoring

# Enable auto-start
sudo systemctl enable boot-monitoring
```

### 2. Light Schedule Checker

**Service Name:** `light-schedule-check.service`  
**Timer Name:** `light-schedule-check.timer`

**Features:**
- Checks light schedule every minute
- Automatically turns lights ON/OFF based on schedule
- Independent of browser/web interface
- Logs all actions to `/var/log/light-schedule-check.log`
- Handles overnight schedules (e.g., ON at 18:00, OFF at 06:00)

**Management Commands:**
```bash
# Check timer status
sudo systemctl status light-schedule-check.timer

# View schedule logs
tail -f /var/log/light-schedule-check.log

# View systemd journal logs
sudo journalctl -u light-schedule-check.service -f

# List next scheduled run
sudo systemctl list-timers light-schedule-check.timer

# Start timer
sudo systemctl start light-schedule-check.timer

# Stop timer
sudo systemctl stop light-schedule-check.timer

# Restart timer
sudo systemctl restart light-schedule-check.timer

# Disable timer (prevent auto-start on boot)
sudo systemctl disable light-schedule-check.timer

# Enable timer (auto-start on boot)
sudo systemctl enable light-schedule-check.timer
```

## Application Access

After installation, access the web interface at:

- **Local:** http://localhost:5000
- **Network:** http://[YOUR_PI_IP]:5000

To find your Raspberry Pi's IP address:
```bash
hostname -I
```

## File Locations

### Application Files
- **Project Directory:** `/home/pi/Boot-Monitoring`
- **Virtual Environment:** `/home/pi/Boot-Monitoring/venv`
- **Environment Config:** `/home/pi/Boot-Monitoring/.env`
- **WSGI Entry:** `/home/pi/Boot-Monitoring/wsgi.py`
- **Gunicorn Config:** `/home/pi/Boot-Monitoring/gunicorn.conf.py`

### Service Files
- **Main Service:** `/etc/systemd/system/boot-monitoring.service`
- **Schedule Service:** `/etc/systemd/system/light-schedule-check.service`
- **Schedule Timer:** `/etc/systemd/system/light-schedule-check.timer`

### Log Files
- **Main Application:** `sudo journalctl -u boot-monitoring`
- **Schedule Checker:** `/var/log/light-schedule-check.log`
- **Schedule Service:** `sudo journalctl -u light-schedule-check.service`

### Scripts
- **Schedule Checker:** `/home/pi/Boot-Monitoring/scripts/check_light_schedule.sh`
- **Port Config:** `/home/pi/Boot-Monitoring/scripts/config.sh`

## Configuration

### Environment Variables (.env)

The installer creates a `.env` file with production settings:

```bash
FLASK_ENV=production
SECRET_KEY=[randomly-generated-key]
DEBUG=false
HOST=0.0.0.0
PORT=5000
```

To modify settings:
```bash
sudo nano /home/pi/Boot-Monitoring/.env
# Then restart the service
sudo systemctl restart boot-monitoring
```

### Light Schedule Configuration

Configure light schedules through the web interface:

1. Navigate to **Settings → Light Schedule Configuration**
2. Click **Edit**
3. Set ON and OFF times (24-hour format)
4. Select active days
5. Click **Save Changes**
6. Enable the schedule on the Dashboard

The schedule will be automatically checked every minute by the systemd timer.

### Port Configuration

To change the Flask application port:

1. Edit the environment file:
   ```bash
   sudo nano /home/pi/Boot-Monitoring/.env
   ```

2. Change the PORT value:
   ```
   PORT=5010
   ```

3. Update Gunicorn config:
   ```bash
   sudo nano /home/pi/Boot-Monitoring/gunicorn.conf.py
   ```

4. Update the bind line:
   ```python
   bind = "0.0.0.0:5010"
   ```

5. Update the schedule checker port config:
   ```bash
   sudo nano /home/pi/Boot-Monitoring/scripts/config.sh
   ```

6. Change FLASK_PORT:
   ```bash
   FLASK_PORT=5010
   ```

7. Update firewall and restart:
   ```bash
   sudo firewall-cmd --add-port=5010/tcp --permanent
   sudo firewall-cmd --reload
   sudo systemctl restart boot-monitoring
   ```

## Troubleshooting

### Service Won't Start

Check the service status and logs:
```bash
sudo systemctl status boot-monitoring
sudo journalctl -u boot-monitoring -n 50 --no-pager
```

Common issues:
- Missing dependencies: Re-run the installer
- Port already in use: Check for other services on port 5000
- Permissions issues: Ensure files are owned by `pi` user

### Can't Access Web Interface

1. Check if service is running:
   ```bash
   sudo systemctl is-active boot-monitoring
   ```

2. Test local connection:
   ```bash
   curl http://localhost:5000
   ```

3. Check firewall:
   ```bash
   sudo firewall-cmd --list-all
   # or for ufw
   sudo ufw status
   ```

4. Verify port is listening:
   ```bash
   sudo netstat -tlnp | grep 5000
   ```

### Light Schedule Not Working

1. Check timer is running:
   ```bash
   sudo systemctl status light-schedule-check.timer
   ```

2. View schedule logs:
   ```bash
   tail -f /var/log/light-schedule-check.log
   ```

3. Check for errors:
   ```bash
   sudo journalctl -u light-schedule-check.service -n 20
   ```

4. Verify schedule is enabled in Dashboard

5. Check Flask app is responding:
   ```bash
   curl -X POST http://localhost:5000/revpi-schedule/check
   ```

### View All Services

```bash
systemctl list-units | grep -E "(boot-monitoring|light-schedule-check)"
```

## Uninstallation

To remove the installation:

```bash
# Stop and disable services
sudo systemctl stop boot-monitoring
sudo systemctl disable boot-monitoring
sudo systemctl stop light-schedule-check.timer
sudo systemctl disable light-schedule-check.timer

# Remove service files
sudo rm /etc/systemd/system/boot-monitoring.service
sudo rm /etc/systemd/system/light-schedule-check.service
sudo rm /etc/systemd/system/light-schedule-check.timer

# Reload systemd
sudo systemctl daemon-reload

# Remove firewall rule
sudo firewall-cmd --remove-port=5000/tcp --permanent
sudo firewall-cmd --reload
# or for ufw
sudo ufw delete allow 5000/tcp

# Optional: Remove application files
sudo rm -rf /home/pi/Boot-Monitoring
sudo rm /var/log/light-schedule-check.log
```

Or use the uninstall script:
```bash
sudo /home/pi/Boot-Monitoring/deployment/uninstall_autostart.sh
```

## Production Recommendations

1. **Security**
   - Change default SECRET_KEY if needed
   - Use HTTPS with reverse proxy (nginx/Apache)
   - Configure proper firewall rules
   - Regular security updates: `sudo apt update && sudo apt upgrade`

2. **Monitoring**
   - Set up log rotation for application logs
   - Monitor service status with monitoring tools
   - Regular backups of configuration and database

3. **Performance**
   - Adjust Gunicorn workers based on CPU cores
   - Configure nginx reverse proxy for better performance
   - Use production database (PostgreSQL/MySQL) for scale

4. **Maintenance**
   - Regular log review
   - Schedule database backups
   - Monitor disk space for logs
   - Keep Python dependencies updated

## Support

For issues or questions:
- Check systemd logs: `sudo journalctl -u boot-monitoring -f`
- Check application logs: `tail -f /var/log/light-schedule-check.log`
- Review service status: `sudo systemctl status boot-monitoring`

## Version Information

- **Installer Version:** 2.0
- **Supported OS:** Debian/Ubuntu/Raspberry Pi OS
- **Python Version:** 3.7+
- **Services:** boot-monitoring, light-schedule-check

---

**Last Updated:** October 27, 2025
