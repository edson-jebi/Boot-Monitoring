# Boot-Monitoring v2 - Changelog & Summary

## Repository Status: ✅ CLEAN & UP-TO-DATE

**Branch:** `v2_branch`  
**Last Sync:** October 29, 2025  
**Status:** All changes committed and pushed to remote

---

## Recent Commits Summary (Latest 5)

### 📅 Commit e9e5920 - October 29, 2025
**feat: Add overnight light schedule support**

**Key Features:**
- ✅ Enhanced schedule logic to support overnight schedules (e.g., ON 18:00, OFF 06:00)
- ✅ Schedule correctly handles schedules that cross midnight
- ✅ Added day validation for overnight schedules (checks yesterday for morning portion)
- ✅ Removed restriction requiring end_time > start_time in schedule service
- ✅ Improved timeline visualization with larger, orange-bordered manual event indicators
- ✅ Added helpful UI tips explaining overnight schedule functionality
- ✅ Added note explaining day selection behavior for overnight schedules

**Files Changed:**
- `app/controllers/revpi_controller.py` - Enhanced check_light_schedule endpoint
- `app/services/schedule_service.py` - Removed time validation restriction
- `templates/bradken-switchos-mockup.html` - UI improvements with user tips

**Example:** Selecting "Wednesday" with ON at 18:00 and OFF at 06:00 will turn lights on Wednesday at 6 PM and off Thursday at 6 AM.

---

### 📅 Commit 13513c1 - October 29, 2025
**chore: Update production configuration files**

**Key Changes:**
- Gunicorn timeout: 30s → 120s (improved stability for long-running operations)
- Gunicorn keepalive: 2s → 5s (better connection persistence)
- Added max_requests_jitter: 50 (prevents thundering herd)
- Enhanced logging configuration (stdout/stderr with info level)
- Updated wsgi.py docstring for clarity

**Files Changed:**
- `gunicorn.conf.py`
- `wsgi.py`

---

### 📅 Commit 4ccbdad - October 29, 2025
**feat: Implement dynamic branding system for multi-brand support**

**Key Features:**
- ✅ Multi-brand architecture supporting BRADKEN and JEBI brands
- ✅ Dynamic logo switching based on APP_BRAND environment variable
- ✅ Brand-specific theme files (theme-jebi.css)
- ✅ Conditional template rendering for logo paths
- ✅ Configuration-driven branding system

**Files Changed:**
- `templates/bradken-switchos-mockup.html` - Dynamic logo loading
- `templates/login.html` - Brand-specific styling
- `static/css/theme-jebi.css` - JEBI brand theme
- Configuration files updated

**Brand Switching:**
```python
# Set in .env file
APP_BRAND=JEBI  # or BRADKEN
```

---

### 📅 Commit 6d4fba7 - October 29, 2025
**feat: Major UI/UX improvements and installation documentation**

**Key Features:**
- ✅ Toast notification system (replaces browser alerts)
- ✅ Browser history management (prevents logout on back button)
- ✅ Timeline improvements with server time synchronization
- ✅ Auto-refresh controls (5s, 10s, 30s, 1min intervals)
- ✅ Floating back-to-top button
- ✅ Sticky header with z-index 1000
- ✅ Comprehensive installation documentation

**Files Added:**
- `INSTALLATION.md` - Quick start guide
- `deployment/README.md` - Detailed deployment documentation

**Files Changed:**
- `templates/bradken-switchos-mockup.html` - Major UI enhancements
- `deployment/simple_install.sh` - Enhanced with 10-step progress indicators

**UI Improvements:**
- Toast notifications with slideIn/slideOut animations
- Timeline with real-time updates from `/system-time` endpoint
- Manual refresh button for timeline
- Auto-refresh dropdown selector

---

### 📅 Commit 2e3c312 - October 29, 2025
**feat: Add Bradken logo to all screen headers and improve UI consistency**

**Key Features:**
- ✅ Bradken logo integrated in all screen headers
- ✅ Improved header consistency across Dashboard, Settings, and Logs screens
- ✅ Relay activation timeline with real database events
- ✅ Timezone configuration support
- ✅ System information display in headers

**Files Changed:**
- `templates/bradken-switchos-mockup.html` - Logo integration, timeline implementation
- `app/controllers/revpi_controller.py` - Enhanced relay activation endpoints
- `static/logos.png` - New logo file

---

## Current Application Architecture

### 🏗️ Project Structure
```
Boot-Monitoring/
├── app/
│   ├── controllers/           # Request handlers
│   │   ├── revpi_controller.py       (RevPi device control, schedules)
│   │   ├── analytics_controller.py   (System analytics)
│   │   ├── config_editor_controller.py (Config management)
│   │   └── service_monitor_controller.py (Service monitoring)
│   ├── services/              # Business logic
│   │   ├── revpi_service.py          (RevPi device operations)
│   │   ├── schedule_service.py       (Light schedule management)
│   │   └── config_service.py         (Configuration management)
│   ├── routes/                # URL routing
│   │   ├── main.py                   (Main routes)
│   │   └── auth.py                   (Authentication)
│   ├── auth/                  # Authentication module
│   ├── utils/                 # Utility functions
│   ├── error_handlers.py      # Error handling
│   └── logging_config.py      # Logging configuration
├── templates/                 # HTML templates
│   ├── bradken-switchos-mockup.html  (Main dashboard)
│   ├── login.html                     (Login page)
│   └── *.html                         (Other templates)
├── static/                    # Static assets
│   ├── css/                           (Stylesheets)
│   │   ├── core.css                   (BRADKEN theme)
│   │   └── theme-jebi.css             (JEBI theme)
│   ├── js/                            (JavaScript)
│   ├── logos.png                      (BRADKEN logo)
│   └── logo_jebi.png                  (JEBI logo)
├── deployment/                # Deployment scripts
│   ├── simple_install.sh              (Automated installation)
│   ├── jebi-web-app.service           (Web app systemd service)
│   └── jebi-schedule-daemon.service   (Schedule daemon service)
├── logs/                      # Application logs (gitignored)
├── config.py                  # Main configuration
├── gunicorn.conf.py           # Production WSGI config
├── wsgi.py                    # WSGI entry point
├── web.py                     # Development server
└── requirements.txt           # Python dependencies
```

### 🎨 Multi-Brand System

**Supported Brands:**
1. **BRADKEN** (Default)
   - Logo: `logos.png`
   - Theme: `core.css`
   - Colors: Blue gradient (#005596 to #003d6b)

2. **JEBI**
   - Logo: `logo_jebi.png`
   - Theme: `theme-jebi.css`
   - Colors: Dark marine blue (#0B2533) with brand red (#F53A1E)

**Configuration:**
```bash
# In .env file
APP_BRAND=JEBI  # or BRADKEN
APP_NAME="JEBI"  # or "Bradken"
```

### 🌙 Light Schedule Features

**Capabilities:**
- ✅ 24-hour format time selection
- ✅ Overnight schedules (crosses midnight)
- ✅ Day-of-week selection (Mon-Sun)
- ✅ Enable/disable toggle
- ✅ Real-time enforcement via cron
- ✅ Smart day validation for overnight schedules

**Schedule Logic:**
- **Normal Schedule:** ON 08:00, OFF 17:00 → Lights on during day
- **Overnight Schedule:** ON 18:00, OFF 06:00 → Lights on during night
  - Day selection refers to when lights turn ON
  - Example: "Wednesday" ON 18:00, OFF 06:00 = Wed 6PM to Thu 6AM

### 🔄 Auto Power Cycle

**Features:**
- ✅ Automatic device monitoring
- ✅ Connectivity-based power cycling
- ✅ Configurable parameters:
  - Monitoring interval (default: 10s)
  - Failed attempts threshold (default: 2)
  - Maximum retry attempts (default: 4)
  - Cooldown period (default: 9s)
- ✅ Service control via systemd
- ✅ Real-time status monitoring

### 📊 Timeline & Analytics

**Power Cycle Events:**
- ✅ Real-time event tracking
- ✅ Database-backed storage
- ✅ Time windows: 1H, 1D, 1W, 1M
- ✅ Event types: Automatic vs Manual
- ✅ Visual timeline with SVG rendering
- ✅ Auto-refresh: Manual, 5s, 10s, 30s, 1min
- ✅ Server time synchronization

**Visual Indicators:**
- 🔵 Automatic events: Filled blue circles
- 🟠 Manual events: Hollow orange circles (larger, more visible)

### 🚀 Production Configuration

**Gunicorn Settings:**
```python
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 120              # Handles long-running operations
keepalive = 5              # Connection persistence
max_requests = 1000        # Worker restart threshold
max_requests_jitter = 50   # Prevents thundering herd
preload_app = True         # Memory optimization
accesslog = "-"            # stdout
errorlog = "-"             # stderr
loglevel = "info"
```

**Systemd Services:**
1. `jebi-web-app.service` - Main Flask application
2. `jebi-schedule-daemon.service` - Light schedule automation
3. `jebi-switchboard-guard.service` - Auto power cycle monitoring

### 📦 Dependencies

**Core:**
- Flask (Web framework)
- Gunicorn (WSGI server)
- SQLite (Database)
- RevPiPyLoad (RevPi hardware interface)
- python-dotenv (Environment management)

**Utilities:**
- pytz (Timezone support)
- requests (HTTP client)

---

## Installation

### Quick Start (New System)
```bash
# Clone repository
git clone https://github.com/edson-jebi/Boot-Monitoring.git
cd Boot-Monitoring

# Run automated installation
chmod +x deployment/simple_install.sh
sudo ./deployment/simple_install.sh

# Configure environment
cp .env.example .env
nano .env  # Set APP_BRAND, APP_NAME, etc.

# Start services
sudo systemctl start jebi-web-app
sudo systemctl start jebi-schedule-daemon
```

### Manual Installation
See `INSTALLATION.md` or `deployment/README.md` for detailed steps.

---

## Configuration Files

### Environment Variables (.env)
```bash
# Application
APP_BRAND=JEBI                    # BRADKEN or JEBI
APP_NAME=JEBI                     # Display name
FLASK_ENV=production              # production or development
SECRET_KEY=your-secret-key-here

# Server
PORT=5000
HOST=0.0.0.0

# Database
DATABASE_PATH=users.db

# Logging
LOG_LEVEL=INFO
```

### System Information (system_info.json)
```json
{
  "system_code": "EX 125",
  "equipment": "Kansanshi",
  "location": "GV0012"
}
```

---

## Git Repository Status

### ✅ All Clean
- Working tree clean
- All changes committed
- Remote branch up-to-date
- No uncommitted files

### 📁 Ignored Files (.gitignore)
- `__pycache__/` - Python bytecode cache
- `venv/` - Virtual environment
- `*.db` - Database files
- `logs/` - Log files
- `.env` - Environment variables
- IDE files (.vscode, .idea)

### 🗑️ Files Safe to Delete (Manual Cleanup)
```bash
# Python cache (regenerated automatically)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Log files (if needed)
rm -rf logs/*.log
```

---

## Testing & Validation

### ✅ Verified Features
1. Multi-brand switching (BRADKEN ↔ JEBI)
2. Overnight light schedules
3. Auto power cycle monitoring
4. Timeline visualization with real events
5. Toast notifications
6. Browser history management
7. Production configuration (120s timeout)
8. Installation automation

### 🧪 Test Commands
```bash
# Check service status
sudo systemctl status jebi-web-app
sudo systemctl status jebi-schedule-daemon

# View logs
journalctl -u jebi-web-app -f
tail -f logs/jebi_web.log

# Test configuration
python -c "from app import create_app; app = create_app('production'); print(app.config)"
```

---

## Next Steps & Recommendations

### 🎯 Immediate Actions
1. ✅ Repository is clean and ready for deployment
2. ✅ All features tested and working
3. ✅ Documentation complete

### 🚀 Future Enhancements
1. **Database Migrations:** Consider using Alembic for schema management
2. **API Documentation:** Add Swagger/OpenAPI documentation
3. **Unit Tests:** Add pytest test suite
4. **Monitoring:** Integrate Prometheus metrics
5. **CI/CD:** Setup GitHub Actions for automated testing
6. **Docker:** Create Docker containers for easier deployment

### 📊 Performance Monitoring
- Monitor Gunicorn worker performance
- Track database query times
- Review log files for errors
- Monitor system resource usage

---

## Support & Documentation

### 📚 Documentation Files
- `README.md` - Project overview
- `INSTALLATION.md` - Quick installation guide
- `deployment/README.md` - Detailed deployment guide
- `DESIGN_SYSTEM.md` - UI/UX design system
- `BRAND_COLORS_REFERENCE.md` - Brand color guidelines

### 🔗 Useful Links
- Repository: https://github.com/edson-jebi/Boot-Monitoring
- Branch: v2_branch
- Issues: https://github.com/edson-jebi/Boot-Monitoring/issues

---

## Version History

### v2.0 - October 29, 2025
- Multi-brand support (BRADKEN/JEBI)
- Overnight light schedules
- Enhanced UI/UX with toast notifications
- Production-ready configuration
- Comprehensive documentation

### v1.0 - Earlier
- Initial Boot-Monitoring application
- Basic RevPi control
- Simple light scheduling
- Authentication system

---

**Document Generated:** October 29, 2025  
**Status:** ✅ Repository Clean & Production Ready  
**Maintainer:** edson-jebi
