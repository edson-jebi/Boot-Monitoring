#!/bin/bash
#
# Light Schedule Check Script
# This script calls the schedule check endpoint to enforce light schedule
# Run this via cron every minute for automatic schedule control
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load configuration
if [ -f "$SCRIPT_DIR/config.sh" ]; then
    source "$SCRIPT_DIR/config.sh"
else
    # Fallback configuration if config.sh doesn't exist
    FLASK_PORT=5010
    API_URL="http://localhost:${FLASK_PORT}/revpi-schedule/check"
    LOG_FILE="/var/log/light-schedule-check.log"
    MAX_LOG_SIZE=10485760
fi

# Rotate log if too large
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Log rotated" > "$LOG_FILE"
fi

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Make the API call
log_message "Checking light schedule..."

response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -w "\nHTTP_CODE:%{http_code}" \
    --max-time 10 \
    "$API_URL" 2>&1)

# Extract HTTP code
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
response_body=$(echo "$response" | sed '/HTTP_CODE:/d')

if [ -z "$http_code" ]; then
    log_message "ERROR: Failed to connect to API"
    exit 1
fi

if [ "$http_code" -eq 200 ]; then
    # Parse response (basic parsing)
    action=$(echo "$response_body" | grep -o '"action":"[^"]*"' | cut -d'"' -f4)
    message=$(echo "$response_body" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$action" = "turned_on" ] || [ "$action" = "turned_off" ]; then
        log_message "ACTION: $action - $message"
    else
        log_message "INFO: $message"
    fi
else
    log_message "ERROR: HTTP $http_code - $response_body"
    exit 1
fi

exit 0
