# Jebi-Switchboard Integration with Analytics

## Overview

The jebi-switchboard service has been successfully integrated with the Boot-Monitoring web application analytics system. All automatic relay activations performed by the jebi-switchboard service are now logged and displayed in the Relay Activation Timeline.

## What Was Implemented

### 1. Web Application API Endpoint

**File:** `app/controllers/revpi_controller.py`

Added a new endpoint `/log-service-activation` that allows the jebi-switchboard service to log relay activations without requiring authentication:

```python
def log_service_activation(self):
    """Log relay activation from jebi-switchboard service"""
    data = request.get_json()
    device_id = data.get('device_id')
    action = data.get('action')

    relay_activation.log_activation(
        device_id=device_id,
        action=action,
        user_id=None,
        username='jebi-switchboard',
        is_automatic=True,
        success=True
    )
```

**File:** `app/routes/main.py`

Registered the endpoint:
```python
main_bp.add_url_rule('/log-service-activation', 'log_service_activation',
                     revpi_controller.log_service_activation, methods=['POST'])
```

### 2. Jebi-Switchboard Service Modifications

**File:** `/home/pi/jebi-switchboard/check_alive_strict_log.py`

Added logging functionality to call the web application API whenever a relay is activated:

```python
import requests

def log_activation_to_webapp(device_id: str, action: str):
    """Log relay activation to the web application API"""
    try:
        response = requests.post(
            'http://localhost:5000/log-service-activation',
            json={'device_id': device_id, 'action': action},
            timeout=2
        )
        if response.status_code == 200:
            logger.debug(f"Logged {device_id} {action} to web app")
        else:
            logger.warning(f"Failed to log to web app: {response.status_code}")
    except Exception as e:
        logger.debug(f"Could not log to web app (non-critical): {e}")
```

Updated the `power_cycle_devices()` function to log every relay activation:

```python
# Turn ON relays (cut power)
if cycle_processor:
    set_relay(RELAY_PROCESSOR, 1)
    log_activation_to_webapp('RelayProcessor', 'on')  # NEW

if cycle_screen:
    set_relay(RELAY_SCREEN, 1)
    log_activation_to_webapp('RelayScreen', 'on')  # NEW

# Wait...
await asyncio.sleep(OFF_SECONDS)

# Turn OFF relays (restore power)
if cycle_processor:
    set_relay(RELAY_PROCESSOR, 0)
    log_activation_to_webapp('RelayProcessor', 'off')  # NEW

if cycle_screen:
    set_relay(RELAY_SCREEN, 0)
    log_activation_to_webapp('RelayScreen', 'off')  # NEW
```

## How It Works

1. **Device Monitoring**: The jebi-switchboard service continuously monitors device health by pinging them
2. **Power Cycling**: When a device is detected as offline, the service power-cycles it by:
   - Turning relay ON (cutting power)
   - Waiting for configured duration
   - Turning relay OFF (restoring power)
3. **Logging**: Each relay activation (ON and OFF) calls the web application API
4. **Database Storage**: The API endpoint stores the activation in the `relay_activations` table with:
   - `username='jebi-switchboard'`
   - `is_automatic=True`
   - `user_id=NULL`
5. **Analytics Display**: The Relay Activation Timeline shows these events as hollow circles (automatic) vs solid circles (manual)

## Database Schema

All activations are stored in the `relay_activations` table:

```sql
CREATE TABLE relay_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,          -- 'RelayProcessor', 'RelayScreen', etc.
    action TEXT NOT NULL,             -- 'on' or 'off'
    user_id INTEGER,                  -- NULL for automatic activations
    username TEXT,                    -- 'jebi-switchboard' for service activations
    is_automatic BOOLEAN DEFAULT 0,   -- 1 for service activations
    success BOOLEAN DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Analytics Dashboard

Access the analytics at: `http://localhost:5000/analytics`

The dashboard displays:
- **Scatterplot**: Time-series visualization of all relay activations
  - Blue solid circles: Manual activations (by users)
  - Blue hollow circles: Automatic activations (by jebi-switchboard)
- **Statistics**:
  - Total Events: All activations
  - Manual: User-initiated activations
  - Automatic: Service-initiated power cycles

## Testing the Integration

### Test API Endpoint
```bash
curl -X POST http://localhost:5000/log-service-activation \
  -H "Content-Type: application/json" \
  -d '{"device_id": "RelayProcessor", "action": "on"}'
```

Expected response:
```json
{"message": "Activation logged", "success": true}
```

### Check Database
```python
import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM relay_activations WHERE is_automatic = 1')
print(f"Automatic activations: {cursor.fetchone()[0]}")
```

### Restart Services
After modifying the code, restart the services:
```bash
# Restart web application
sudo systemctl restart boot-monitoring.service

# Restart jebi-switchboard (if running as service)
sudo systemctl restart jebi-switchboard-guard.service
```

## Current Statistics

As of integration completion:
- **Total activations**: 169
- **Manual activations**: 108
- **Automatic activations**: 61 (from jebi-switchboard)

## Requirements

- Python `requests` library must be installed in the jebi-switchboard environment
- Boot-Monitoring web application must be running on port 5000
- Database must have `relay_activations` table (created by `init_database()`)

## Notes

- The API endpoint does not require authentication to allow the service to log activations
- Failed API calls are logged but do not prevent the service from functioning
- The integration is non-blocking and won't delay power cycle operations
- All timestamps are stored in UTC in the database