#!/bin/bash

# Simple Boot-Monitoring Installer
# Installs Flask app with virtual environment and systemd service

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_info "Starting simple Boot-Monitoring installation..."

# Install system dependencies
print_info "Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# Setup virtual environment as pi user
print_info "Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $APP_USER python3 -m venv "$VENV_DIR"
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
sudo -u $APP_USER "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u $APP_USER "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Install Gunicorn for production
print_info "Installing Gunicorn for production..."
sudo -u $APP_USER "$VENV_DIR/bin/pip" install gunicorn python-dotenv

# Generate secure secret key for production
print_info "Generating secure production configuration..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create production environment file
sudo -u $APP_USER cat > "$APP_DIR/.env" << EOF
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
DEBUG=false
HOST=0.0.0.0
PORT=5000
EOF

# Set secure permissions on environment file
chmod 600 "$APP_DIR/.env"
chown $APP_USER:$APP_USER "$APP_DIR/.env"

# Create production WSGI entry point
sudo -u $APP_USER cat > "$APP_DIR/wsgi.py" << 'EOF'
#!/usr/bin/env python3
"""Production WSGI Entry Point"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask application in production mode
application = create_app('production')

if __name__ == "__main__":
    application.run()
EOF

# Create Gunicorn configuration
sudo -u $APP_USER cat > "$APP_DIR/gunicorn.conf.py" << EOF
# Gunicorn production configuration
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
EOF

# Create systemd service
print_info "Creating systemd service..."
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

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_info "Enabling service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Start the service
print_info "Starting service..."
systemctl start $SERVICE_NAME

# Check if service started successfully
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service started successfully!"
    print_info "Application should be running on http://$(hostname -I | awk '{print $1}'):5000"
    print_info "Local access: http://localhost:5000"
else
    print_error "Service failed to start"
    systemctl status $SERVICE_NAME
    exit 1
fi

# Configure firewall to allow port 5000
print_info "Configuring firewall to allow port 5000..."
if command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active --quiet firewalld; then
    print_info "Firewalld detected, adding port 5000..."
    firewall-cmd --add-port=5000/tcp --permanent
    firewall-cmd --reload
    print_success "Port 5000 added to firewall"
elif command -v ufw >/dev/null 2>&1; then
    print_info "UFW detected, adding port 5000..."
    ufw allow 5000/tcp
    print_success "Port 5000 added to UFW firewall"
else
    print_info "No supported firewall detected (firewalld/ufw)"
    print_info "You may need to manually configure your firewall to allow port 5000"
fi

print_success "Installation completed!"
echo
echo "════════════════════════════════════════════════"
echo "    Boot-Monitoring Production Installation      "
echo "════════════════════════════════════════════════"
echo
echo " Production Features:"
echo "   • Virtual environment: $VENV_DIR"
echo "   • Gunicorn WSGI server (2 workers)"
echo "   • Secure environment configuration"
echo "   • Systemd service management"
echo "   • Firewall configured for port 5000"
echo
echo "🔧 Service Management:"
echo "   Status:  systemctl status $SERVICE_NAME"
echo "   Logs:    journalctl -fu $SERVICE_NAME"
echo "   Stop:    systemctl stop $SERVICE_NAME"
echo "   Start:   systemctl start $SERVICE_NAME"
echo "   Restart: systemctl restart $SERVICE_NAME"
echo
echo "🔥 Firewall Management:"
echo "   List rules: firewall-cmd --list-all"
echo "   Remove port: firewall-cmd --remove-port=5000/tcp --permanent && firewall-cmd --reload"
echo "   Add port: firewall-cmd --add-port=5000/tcp --permanent && firewall-cmd --reload"
echo
echo " Application Access:"
echo "   URL: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Local: http://localhost:5000"
echo
echo " Important Files:"
echo "   Environment: $APP_DIR/.env"
echo "   WSGI Entry: $APP_DIR/wsgi.py"
echo "   Service: /etc/systemd/system/$SERVICE_NAME.service"
echo
