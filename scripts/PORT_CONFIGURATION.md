# Light Schedule Configuration Guide

## Port Configuration

The light schedule system needs to know which port your Flask application is running on.

### Configuration File: `scripts/config.sh`

Edit this file to set the correct port:

```bash
# Flask application port
FLASK_PORT=5010  # Change this to match your setup
```

### Common Port Configurations:

**Development Mode** (web.py with debug=True):
- Usually runs on port **5010** or **5001**
- Check `web.py` for the port number in: `app.run(host='0.0.0.0', port=XXXX)`

**Production Mode** (with Gunicorn):
- Usually runs on port **5000**
- Check `gunicorn.conf.py` for the bind address

### How to Update:

1. **Find your Flask app port:**
   ```bash
   # Check which port Flask is running on
   netstat -tulpn | grep python
   # or
   ss -tulpn | grep python
   ```

2. **Edit config.sh:**
   ```bash
   cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
   nano config.sh
   ```

3. **Update FLASK_PORT:**
   ```bash
   FLASK_PORT=5010  # Change to your port (5000, 5010, 5001, etc.)
   ```

4. **Test the configuration:**
   ```bash
   ./check_light_schedule.sh
   tail -10 /var/log/light-schedule-check.log
   ```

### Automatic Detection:

The script will automatically use:
- Port from `config.sh` (if file exists)
- Port 5010 as fallback (if config.sh doesn't exist)

### Troubleshooting:

If you see **HTTP 404 errors** in the log:
1. Check Flask app is running: `ps aux | grep "python.*web.py"`
2. Check the port: `netstat -tulpn | grep python`
3. Update `scripts/config.sh` with the correct port
4. Restart the schedule service:
   - **Cron**: `crontab -l` (it will pick up changes automatically)
   - **Systemd timer**: `sudo systemctl restart light-schedule-check.timer`

### Example Configurations:

**For Development (web.py):**
```bash
FLASK_PORT=5010
```

**For Production (Gunicorn on default port):**
```bash
FLASK_PORT=5000
```

**For Custom Setup:**
```bash
FLASK_PORT=8080  # Use your custom port
```
