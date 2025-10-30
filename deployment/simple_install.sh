#!/bin/bash

# Boot-Monitoring Complete Installer for RevPi
# This script installs the complete Boot-Monitoring application on a new RevPi device
# Compatible with Revolution Pi devices

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root. Use: sudo $0"
    exit 1
fi

# Configuration
APP_USER="pi"
APP_DIR="/home/pi/Boot-Monitoring"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="boot-monitoring"

echo "════════════════════════════════════════════════"
echo " Boot-Monitoring Installation for RevPi"
echo "════════════════════════════════════════════════"
echo

# Check if application directory exists
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found at $APP_DIR"
    print_info "Please clone or copy the Boot-Monitoring repository to $APP_DIR first"
    print_info "Example: git clone <repository-url> $APP_DIR"
    exit 1
fi

print_step "1/10 - Updating system packages..."
apt-get update
apt-get upgrade -y

print_step "2/10 - Installing system dependencies..."
apt-get install -y python3 python3-pip python3-venv git curl

# Install optional but recommended packages
apt-get install -y python3-dev build-essential libssl-dev libffi-dev || true

print_step "3/10 - Setting up Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    print_info "Virtual environment already exists, recreating..."
    rm -rf "$VENV_DIR"
fi
sudo -u $APP_USER python3 -m venv "$VENV_DIR"

print_step "4/10 - Installing Python dependencies..."
sudo -u $APP_USER "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
sudo -u $APP_USER "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Install Gunicorn and dotenv for production
print_info "Installing production dependencies..."
sudo -u $APP_USER "$VENV_DIR/bin/pip" install gunicorn python-dotenv

print_step "5/10 - Generating secure production configuration..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create production environment file
sudo -u $APP_USER cat > "$APP_DIR/.env" << EOF
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DEBUG=false
HOST=0.0.0.0
PORT=5000
APP_BRAND=BRADKEN
SESSION_TIMEOUT=3600
COMMAND_TIMEOUT=10
DEFAULT_USERNAME=bradken
DEFAULT_PASSWORD=adminBradken25
EOF

# Set secure permissions on environment file
chmod 600 "$APP_DIR/.env"
chown $APP_USER:$APP_USER "$APP_DIR/.env"
print_success "Secure environment configuration created"

print_step "6/10 - Creating production WSGI entry point..."
sudo -u $APP_USER cat > "$APP_DIR/wsgi.py" << 'EOF'
#!/usr/bin/env python3
"""Production WSGI Entry Point for Boot-Monitoring"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application in production mode
application = create_app('production')

if __name__ == "__main__":
    application.run()
EOF

print_step "7/10 - Creating Gunicorn configuration..."
sudo -u $APP_USER cat > "$APP_DIR/gunicorn.conf.py" << EOF
# Gunicorn Production Configuration for Boot-Monitoring
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
EOF

print_step "8/10 - Creating systemd service for main application..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Boot-Monitoring Flask Application (Production)
After=network.target

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
TimeoutStopSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
print_success "Main application service created and enabled"

print_step "9/10 - Setting up Light Schedule Automation..."
SCRIPTS_DIR="$APP_DIR/scripts"
CHECK_SCRIPT="$SCRIPTS_DIR/check_light_schedule.sh"

if [ -f "$CHECK_SCRIPT" ]; then
    # Make the check script executable
    chmod +x "$CHECK_SCRIPT"

    # Create log directory
    mkdir -p /var/log
    touch /var/log/light-schedule-check.log
    chown $APP_USER:$APP_USER /var/log/light-schedule-check.log

    # Create systemd service for schedule check
    cat > /etc/systemd/system/light-schedule-check.service << EOF
[Unit]
Description=Light Schedule Check
After=network.target $SERVICE_NAME.service

[Service]
Type=oneshot
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$CHECK_SCRIPT
StandardOutput=append:/var/log/light-schedule-check.log
StandardError=append:/var/log/light-schedule-check.log

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd timer for schedule check
    cat > /etc/systemd/system/light-schedule-check.timer << EOF
[Unit]
Description=Light Schedule Check Timer (runs every minute)
Requires=light-schedule-check.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF

    # Reload systemd
    systemctl daemon-reload

    # Enable and start the timer
    systemctl enable light-schedule-check.timer
    systemctl start light-schedule-check.timer

    print_success "Light Schedule Automation installed and started"
else
    print_info "Light schedule check script not found, skipping..."
fi

# Create system_info.json file if it doesn't exist
if [ ! -f "$APP_DIR/system_info.json" ]; then
    print_info "Creating system_info.json with default values..."
    sudo -u $APP_USER cat > "$APP_DIR/system_info.json" << EOF
{
  "system_code": "",
  "equipment": "",
  "location": ""
}
EOF
    chmod 644 "$APP_DIR/system_info.json"
    chown $APP_USER:$APP_USER "$APP_DIR/system_info.json"
fi

print_step "10/10 - Configuring firewall..."
if command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active --quiet firewalld; then
    print_info "Firewalld detected, adding port 5000..."
    firewall-cmd --add-port=5000/tcp --permanent
    firewall-cmd --reload
    print_success "Port 5000 added to firewalld"
elif command -v ufw >/dev/null 2>&1; then
    print_info "UFW detected, adding port 5000..."
    ufw allow 5000/tcp
    print_success "Port 5000 added to UFW"
else
    print_info "No firewall detected (firewalld/ufw)"
    print_info "If you have a firewall, manually allow port 5000/tcp"
fi

# Start the main application service
print_info "Starting Boot-Monitoring service..."
systemctl start $SERVICE_NAME

# Wait and check if service started successfully
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service started successfully!"
else
    print_error "Service failed to start. Checking logs..."
    journalctl -u $SERVICE_NAME -n 50 --no-pager
    exit 1
fi

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo
echo "════════════════════════════════════════════════"
echo " ✓ Installation Completed Successfully!"
echo "════════════════════════════════════════════════"
echo
echo "📱 Application Access:"
echo "   Network:  http://$IP_ADDR:5000"
echo "   Local:    http://localhost:5000"
echo
echo "🔐 Default Login:"
echo "   Username: bradken"
echo "   Password: adminBradken25"
echo "   ⚠️  Please change password after first login!"
echo
echo "🔧 Service Management:"
echo "   Status:   systemctl status $SERVICE_NAME"
echo "   Logs:     journalctl -fu $SERVICE_NAME"
echo "   Stop:     sudo systemctl stop $SERVICE_NAME"
echo "   Start:    sudo systemctl start $SERVICE_NAME"
echo "   Restart:  sudo systemctl restart $SERVICE_NAME"
echo
echo "⏰ Light Schedule Automation:"
echo "   Timer Status:  systemctl status light-schedule-check.timer"
echo "   Schedule Logs: tail -f /var/log/light-schedule-check.log"
echo "   List Timers:   systemctl list-timers"
echo
echo "📁 Important Files:"
echo "   App Directory:    $APP_DIR"
echo "   Environment:      $APP_DIR/.env"
echo "   Database:         $APP_DIR/users.db"
echo "   System Info:      $APP_DIR/system_info.json"
echo "   Service File:     /etc/systemd/system/$SERVICE_NAME.service"
echo "   Schedule Service: /etc/systemd/system/light-schedule-check.service"
echo "   Schedule Timer:   /etc/systemd/system/light-schedule-check.timer"
echo
echo "📚 Next Steps:"
echo "   1. Open http://$IP_ADDR:5000 in your browser"
echo "   2. Login with default credentials"
echo "   3. Configure System Information in Settings"
echo "   4. Set up Network Configuration (IP addresses)"
echo "   5. Configure Auto Power Cycle settings"
echo "   6. Set up Light Schedule if needed"
echo "   7. Configure timezone in Settings"
echo
echo "💡 Useful Commands:"
echo "   View all logs:        journalctl -u $SERVICE_NAME --no-pager"
echo "   Clear database:       rm $APP_DIR/users.db (will recreate on restart)"
echo "   Update application:   cd $APP_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
echo "   Uninstall:            sudo systemctl stop $SERVICE_NAME && sudo systemctl disable $SERVICE_NAME"
echo
echo "════════════════════════════════════════════════"
echo
