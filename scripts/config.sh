#!/bin/bash
#
# Configuration file for light schedule scripts
# This file is sourced by check_light_schedule.sh
#

# Flask application port
# Set this to match your web.py configuration:
# - Development: typically 5010 (with debug=True)
# - Production: typically 5000 (with gunicorn)
FLASK_PORT=5010

# API endpoint
API_URL="http://localhost:${FLASK_PORT}/revpi-schedule/check"

# Log file location
LOG_FILE="/var/log/light-schedule-check.log"

# Maximum log file size before rotation (10MB)
MAX_LOG_SIZE=10485760
