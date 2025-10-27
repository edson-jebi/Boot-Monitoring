# Light Schedule System - Setup Complete ✅

## Summary of Fixes

We've resolved the critical bugs that prevented the light schedule from working automatically:

### 🐛 **Issues Fixed:**

1. **Logic Bug - Time Swap (CRITICAL)**
   - Frontend was incorrectly swapping ON/OFF times before saving to database
   - Backend was misinterpreting overnight schedules
   - **Fix**: Store actual times (start_time = ON, end_time = OFF), backend handles logic correctly

2. **Missing Route Registration (CRITICAL)**
   - `/revpi-schedule/check` endpoint was defined but never registered in blueprints
   - **Fix**: Added route registration in `app/routes/main.py`

3. **Port Mismatch**
   - Cron script was calling port 5000, Flask running on port 5010
   - **Fix**: Created `scripts/config.sh` for easy port configuration

### ✅ **Files Modified:**

1. **app/routes/main.py**
   - Added: `main_bp.add_url_rule('/revpi-schedule/check', ...)`

2. **app/controllers/revpi_controller.py**
   - Fixed: Overnight schedule logic in `check_schedule()` method
   - Now correctly handles: ON=18:00, OFF=06:00 (overnight)

3. **templates/bradken-switchos-mockup.html**
   - Removed time-swapping logic from frontend
   - `saveScheduleConfiguration()` now stores actual times
   - `isWithinScheduleTime()` correctly handles overnight schedules

4. **scripts/check_light_schedule.sh**
   - Now loads configuration from `config.sh`
   - Automatic fallback to port 5010 if config missing

5. **scripts/config.sh** (NEW)
   - Centralized configuration for Flask port
   - Easy to update for development vs production

### 📋 **How It Works Now:**

1. **User configures schedule** (e.g., ON at 18:00, OFF at 06:00)
2. **Frontend saves** actual times to database:
   - `start_time = "18:00"` (lights ON)
   - `end_time = "06:00"` (lights OFF)
3. **Backend endpoint** (`/revpi-schedule/check`):
   - Reads schedule from database
   - Checks if current time is within ON period
   - Toggles relay if needed
4. **Automatic execution**:
   - **Option A**: Cron job runs every minute
   - **Option B**: Systemd timer runs every minute
   - **Option C**: Frontend polling (60 seconds) when browser open

### 🚀 **Installation:**

**Quick Start (Auto-detects cron vs systemd):**
```bash
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring/scripts
sudo ./quick_start.sh
```

**Manual - Cron:**
```bash
./install_cron.sh
```

**Manual - Systemd Timer:**
```bash
sudo ./install_systemd_timer.sh
```

### ⚙️ **Configuration:**

**Set Flask Port** (`scripts/config.sh`):
```bash
# Development mode (web.py)
FLASK_PORT=5010

# Production mode (gunicorn)
FLASK_PORT=5000
```

**Verify Configuration:**
```bash
# Check what port Flask is running on
netstat -tulpn | grep python

# Test the endpoint
curl -X POST http://localhost:5010/revpi-schedule/check

# Check logs
tail -f /var/log/light-schedule-check.log
```

### 📊 **Testing:**

1. **Start Flask app:**
   ```bash
   cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring
   source venv/bin/activate
   python3 web.py
   ```

2. **Configure schedule in web UI:**
   - Go to Settings → Light Schedule
   - Set ON time: `18:00`
   - Set OFF time: `06:00`
   - Select days: All days
   - Save settings

3. **Enable schedule:**
   - Go to Dashboard
   - Toggle "Light Schedule" to ON
   - Lights will turn ON/OFF immediately based on current time

4. **Verify automatic operation:**
   ```bash
   # Watch the logs
   tail -f /var/log/light-schedule-check.log
   
   # You should see entries every minute:
   # 2025-10-27 18:00:00 - Checking light schedule...
   # 2025-10-27 18:00:00 - ACTION: turned_on - Light turned ON per schedule
   ```

### 🔧 **Troubleshooting:**

**Issue**: HTTP 404 errors in log
- **Cause**: Flask app not running or wrong port
- **Fix**: 
  ```bash
  ps aux | grep "python.*web.py"
  netstat -tulpn | grep python
  # Update scripts/config.sh with correct port
  ```

**Issue**: Lights don't change at scheduled time
- **Cause**: Schedule not enabled or wrong day/time
- **Fix**: Check web UI settings, verify current day is selected

**Issue**: Cron not working
- **Cause**: crontab command not found
- **Fix**: Use systemd timer instead: `sudo ./install_systemd_timer.sh`

### 📁 **Important Files:**

- `scripts/config.sh` - Port configuration
- `scripts/check_light_schedule.sh` - Main check script
- `/var/log/light-schedule-check.log` - Log file
- `app/routes/main.py` - Route registration
- `app/controllers/revpi_controller.py` - Schedule logic
- `dev_users.db` - Database with schedules table

### 🎯 **Next Steps:**

1. ✅ **Fixed**: Logic bugs
2. ✅ **Fixed**: Missing route registration  
3. ✅ **Fixed**: Port configuration
4. **TODO**: Restart Flask app to load new routes
5. **TODO**: Install cron or systemd timer
6. **TODO**: Test automatic schedule enforcement

---

## Quick Command Reference:

```bash
# Start Flask (development)
cd /home/pi/Boot-Monitoring_Mockup/Boot-Monitoring
source venv/bin/activate
python3 web.py

# Install scheduler
cd scripts
sudo ./quick_start.sh

# Check status
systemctl status light-schedule-check.timer  # Systemd
crontab -l  # Cron

# View logs
tail -f /var/log/light-schedule-check.log

# Test endpoint
curl -X POST http://localhost:5010/revpi-schedule/check

# Check Flask port
netstat -tulpn | grep python
```

---

**Status**: All code fixes complete ✅  
**Remaining**: Flask restart + scheduler installation
