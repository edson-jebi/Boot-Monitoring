# Auto Power Cycle and Network Configuration Integration

## Summary
Integrated both Auto Power Cycle Configuration and Network Configuration sections with the actual switchboard configuration file (`/home/pi/jebi-switchboard/config/strict_log_config.json`). The forms now load real values and save changes back to the file. Auto Power Cycle changes trigger an automatic service restart, while Network Configuration changes do not require a restart.

## Changes Made

### 1. Backend (RevPiController)

#### Updated Endpoints:
- **GET `/switchboard-config`** - Retrieves current configuration from JSON file
  - Returns: CHECK_INTERVAL_SEC, FAIL_WINDOW, MAX_POWER_CYCLES, REBOOT_WAIT_SEC
  - **NEW**: Returns RelayScreen.ip and RelayProcessor.ip
  
- **POST `/switchboard-config/update`** - Updates configuration
  - Accepts: CHECK_INTERVAL_SEC, FAIL_WINDOW, MAX_POWER_CYCLES, REBOOT_WAIT_SEC
  - **NEW**: Accepts RelayScreen_ip and RelayProcessor_ip
  - Updates the JSON file with all changes
  - **Smart Restart**: Only restarts `jebi-switchboard-guard.service` if monitoring parameters changed
  - Network config changes do NOT trigger service restart
  - Returns success/failure status

#### Files Modified:
- `/home/pi/Boot-Monitoring/app/controllers/revpi_controller.py`
  - Added `get_switchboard_config()` method
  - Added `update_switchboard_config()` method
  - Registered routes in `_register_routes()`

- `/home/pi/Boot-Monitoring/app/routes/main.py`
  - Registered new routes in main blueprint

### 2. Frontend (bradken-switchos-mockup.html)

#### Auto Power Cycle Form Updates:
Changed from dropdown selects to number inputs with proper labeling:
- **Monitoring Interval** → `<input type="number">` for CHECK_INTERVAL_SEC (seconds)
- **Failed Attempts Threshold** → `<input type="number">` for FAIL_WINDOW
- **Maximum Retry Attempts** → `<input type="number">` for MAX_POWER_CYCLES
- **Cooldown Period** → `<input type="number">` for REBOOT_WAIT_SEC (seconds)

#### Network Configuration Form:
IP address inputs connected to configuration file:
- **Screen IP Address** → Loads/saves RelayScreen.ip
- **Processor IP Address** → Loads/saves RelayProcessor.ip

#### JavaScript Functions:
- **`loadSwitchboardConfig()`** - Fetches config from backend and populates ALL form fields
  - Called on page load
  - Updates Auto Power Cycle fields (4 configuration values)
  - **NEW**: Updates Network Configuration fields (2 IP addresses)
  
- **Updated `saveSettings()`** - Added handlers for both sections
  - **autoPowerCycle section:**
    - Validates all input values (must be >= 1)
    - Sends POST request to `/switchboard-config/update`
    - Shows loading spinner during save
    - Displays success/error messages
    - Restarts service automatically on backend
  
  - **NEW network section:**
    - Validates IP address format (xxx.xxx.xxx.xxx)
    - Sends POST request to `/switchboard-config/update`
    - Shows loading spinner during save
    - Displays success/error messages
    - No service restart needed for IP changes

### 3. System Configuration

#### Sudo Permissions:
Added sudoers rule to allow pi user to restart the service without password:
```bash
# File: /etc/sudoers.d/jebi-switchboard-guard
pi ALL=(ALL) NOPASSWD: /bin/systemctl restart jebi-switchboard-guard.service
```

This allows the web application to restart the service after configuration changes.

## Configuration File Mapping

### Auto Power Cycle Configuration
| Form Field | JSON Key | Description |
|------------|----------|-------------|
| Monitoring Interval | CHECK_INTERVAL_SEC | How often to check device connectivity (seconds) |
| Failed Attempts Threshold | FAIL_WINDOW | Number of failed attempts before power cycling |
| Maximum Retry Attempts | MAX_POWER_CYCLES | Maximum number of power cycle retries |
| Cooldown Period | REBOOT_WAIT_SEC | Wait time before attempting another cycle (seconds) |

### Network Configuration
| Form Field | JSON Key | Current Value | Description |
|------------|----------|---------------|-------------|
| Screen IP Address | RelayScreen.ip | 192.168.1.143 | IP address for the display screen |
| Processor IP Address | RelayProcessor.ip | 192.168.1.142 | IP address for the processing unit |

## Workflow

### 1. **Page Load:**
   - `loadSwitchboardConfig()` fetches current values from `/switchboard-config`
   - Form fields are populated with real values from JSON file
   - Both Auto Power Cycle and Network Configuration sections are loaded

### 2. **Edit Mode:**
   - User clicks "Edit" button on either section
   - Form fields become enabled for that section
   - User modifies values

### 3. **Save Changes:**

   **For Auto Power Cycle Configuration:**
   - User clicks "Save Changes"
   - Confirmation dialog appears
   - JavaScript validates all values (must be positive integers)
   - POST request sent to `/switchboard-config/update` with monitoring parameters
   - Backend:
     - Updates `/home/pi/jebi-switchboard/config/strict_log_config.json`
     - Runs `sudo systemctl restart jebi-switchboard-guard.service`
   - Success message displayed: "Configuration updated and service restarted successfully"
   - Form returns to read-only mode

   **For Network Configuration:**
   - User clicks "Save Changes"
   - Confirmation dialog appears
   - JavaScript validates IP address format (xxx.xxx.xxx.xxx)
   - POST request sent to `/switchboard-config/update` with IP addresses
   - Backend:
     - Updates `/home/pi/jebi-switchboard/config/strict_log_config.json`
     - **NO service restart** (changes take effect on next device power cycle)
   - Success message displayed: "Network configuration updated successfully"
   - Form returns to read-only mode

## Testing

### Test Auto Power Cycle Configuration Load:
1. Open Settings page
2. Auto Power Cycle Configuration should show current values from config file
3. Check browser console for "Switchboard configuration loaded" message

### Test Auto Power Cycle Configuration Save:
1. Click "Edit" on Auto Power Cycle Configuration
2. Change any value (e.g., Monitoring Interval to 20)
3. Click "Save Changes"
4. Confirm in dialog
5. Should see success message with "service restarted"
6. Verify config file updated:
   ```bash
   cat /home/pi/jebi-switchboard/config/strict_log_config.json
   ```
7. Verify service restarted:
   ```bash
   sudo systemctl status jebi-switchboard-guard.service
   ```

### Test Network Configuration Load:
1. Open Settings page
2. Network Configuration should show IP addresses from config file:
   - Screen: 192.168.1.143
   - Processor: 192.168.1.142

### Test Network Configuration Save:
1. Click "Edit" on Network Configuration
2. Change an IP address (e.g., Screen to 192.168.1.150)
3. Click "Save Changes"
4. Confirm in dialog
5. Should see success message (NO service restart mentioned)
6. Verify config file updated:
   ```bash
   cat /home/pi/jebi-switchboard/config/strict_log_config.json | grep -A 2 "RelayScreen"
   ```
7. Service should NOT have restarted (check timestamp):
   ```bash
   sudo systemctl status jebi-switchboard-guard.service | grep Active
   ```

## Current Configuration Values

From `/home/pi/jebi-switchboard/config/strict_log_config.json`:

**Auto Power Cycle Parameters:**
- CHECK_INTERVAL_SEC: 15 seconds (recently changed from 10)
- FAIL_WINDOW: 2 attempts
- MAX_POWER_CYCLES: 4 retries
- REBOOT_WAIT_SEC: 9 seconds
- OFF_SECONDS: 10 seconds (not editable in UI)
- STARTUP_DELAY_SEC: 20 seconds (not editable in UI)

**Network Configuration:**
- RelayScreen.ip: 192.168.1.143
- RelayScreen.name: "RelayScreen"
- RelayProcessor.ip: 192.168.1.142
- RelayProcessor.name: "RelayProcessor"

## Error Handling

- **File not found:** Returns 404 with error message
- **Invalid JSON:** Returns 500 with parse error
- **Invalid values:** Returns 400 with validation error
- **Service restart failure:** Returns 500 but config is still saved
- **Permission denied:** Returns 403 with permission error

All errors are logged to `/home/pi/Boot-Monitoring/logs/jebi_web.log`

## Security Notes

- Configuration updates require login (`@login_required` decorator)
- All actions are logged with user information
- Sudo permissions are restricted to specific service restart command only
- Input validation prevents invalid values from being saved

## Files Modified

1. `/home/pi/Boot-Monitoring/app/controllers/revpi_controller.py`
2. `/home/pi/Boot-Monitoring/app/routes/main.py`
3. `/home/pi/Boot-Monitoring/templates/bradken-switchos-mockup.html`
4. `/etc/sudoers.d/jebi-switchboard-guard` (new file)

## Service Status

- Gunicorn web server: Running on port 5000
- jebi-switchboard-guard.service: Can be restarted via web interface
- Configuration changes take effect immediately after service restart
