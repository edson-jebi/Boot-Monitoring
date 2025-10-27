# Light Schedule Automatic Control - Implementation Guide

## Overview
The light schedule system now automatically controls the RelayLight device based on configured ON/OFF times without requiring a separate daemon service.

## How It Works

### Backend Component
**New Endpoint:** `/revpi-schedule/check` (POST)

Located in: `app/controllers/revpi_controller.py`

**Function:** `check_schedule()`

This endpoint:
1. Retrieves the light schedule from the database
2. Checks if the schedule is enabled
3. Verifies if today is a scheduled day
4. Determines if the light should be ON or OFF based on current time
5. Compares with actual relay state
6. Toggles the relay if needed to match the schedule

**Key Features:**
- No login required (called automatically by frontend)
- Handles overnight schedules (e.g., 18:00 to 06:00)
- Checks day of week against scheduled days
- Only toggles when state doesn't match schedule
- Logs all actions for audit trail

### Frontend Component
**Location:** `templates/bradken-switchos-mockup.html`

**Function:** `checkLightSchedule()`

**Polling Interval:** Every 60 seconds (1 minute)

The frontend:
1. Calls `/revpi-schedule/check` every minute
2. Only runs when `appState.ledScheduleEnabled` is true
3. Refreshes device status display after any state change
4. Logs schedule actions to console

## Schedule Behavior

### Example 1: Daytime Schedule
- **ON Time:** 08:00
- **OFF Time:** 17:00
- **Behavior:** Light is ON between 08:00-16:59, OFF otherwise

### Example 2: Overnight Schedule
- **ON Time:** 18:00  
- **OFF Time:** 06:00
- **Behavior:** Light is ON from 18:00 until 05:59 next morning, OFF during day

### Example 3: Day Selection
- **Days:** Monday, Wednesday, Friday
- **Behavior:** Schedule only active on selected days, light OFF on other days

## User Experience

1. **Setting Schedule:**
   - User goes to Settings → Light Schedule Configuration
   - Sets ON time, OFF time, and days
   - Clicks "Save Changes"
   - System immediately sets relay to correct state for current time

2. **Enabling Schedule:**
   - User toggles "Light Schedule" ON
   - System immediately checks current time and sets relay appropriately
   - Every minute thereafter, system verifies relay matches schedule

3. **Automatic Operation:**
   - User doesn't need to do anything
   - System automatically:
     - Turns light ON at scheduled ON time
     - Turns light OFF at scheduled OFF time
     - Respects day selections
     - Maintains state even if page is refreshed

## Technical Details

### Database Schema
```sql
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL UNIQUE,
    start_time TEXT NOT NULL,  -- HH:MM format
    end_time TEXT NOT NULL,    -- HH:MM format
    days TEXT,                 -- Comma-separated: mon,tue,wed...
    enabled INTEGER DEFAULT 0, -- 1 = enabled, 0 = disabled
    created_at TEXT,
    updated_at TEXT
);
```

### Time Storage Convention
For overnight schedules where lights ON at 18:00 and OFF at 06:00:
- Database stores: `start_time='06:00', end_time='18:00'` (swapped)
- Display shows: `ON: 18:00, OFF: 06:00` (actual user intent)
- Logic handles both correctly

### Polling Advantages Over Daemon
1. **Simpler:** No systemd service to manage
2. **No Installation:** Works immediately without setup
3. **Browser-Based:** Runs when user has app open
4. **Easy Debugging:** See logs in browser console
5. **Cross-Platform:** Works on any system running the Flask app

### Polling Limitations
1. **Browser Dependent:** Only works when browser has page open
2. **1-Minute Granularity:** Can be up to 60 seconds late
3. **Multiple Tabs:** Each open tab will call the endpoint

### For Production Use
For 24/7 automatic operation without browser dependency, consider:
- Using the provided `schedule_daemon.py` as a systemd service
- Or setting up a cron job to call the endpoint
- Or using a task scheduler like Celery

## Testing

### Test Case 1: Enable Schedule During ON Time
1. Set schedule: ON 14:00, OFF 16:00
2. Current time: 14:30
3. Enable schedule
4. **Expected:** Light turns ON immediately

### Test Case 2: Enable Schedule During OFF Time
1. Set schedule: ON 14:00, OFF 16:00
2. Current time: 10:00
3. Enable schedule
4. **Expected:** Light turns OFF immediately

### Test Case 3: Transition to ON Time
1. Schedule enabled: ON 14:00, OFF 16:00
2. Current time: 13:59
3. Wait 1 minute
4. **Expected:** Light turns ON at 14:00 (within 60 seconds)

### Test Case 4: Day Selection
1. Set schedule: Monday only, ON 08:00, OFF 17:00
2. Current time: Tuesday 10:00
3. Enable schedule
4. **Expected:** Light stays OFF (not a scheduled day)

## Troubleshooting

**Schedule not working:**
1. Check browser console for errors
2. Verify schedule is enabled (toggle switch ON)
3. Check current day is in selected days
4. Verify times are set correctly
5. Check network tab for `/revpi-schedule/check` calls

**Light not toggling at scheduled time:**
1. Ensure browser page is open
2. Check console for "Schedule check:" messages
3. Verify 60-second intervals between checks
4. Check backend logs for any errors

**Manual control not working:**
1. Disable schedule first
2. Then use manual toggle
3. Schedule takes priority when enabled

## API Reference

### Check Schedule
```http
POST /revpi-schedule/check
Content-Type: application/json

Response (no action needed):
{
    "success": true,
    "action": "none",
    "message": "Light already ON (correct state)"
}

Response (light turned on):
{
    "success": true,
    "action": "turned_on",
    "message": "Light turned ON per schedule"
}

Response (light turned off):
{
    "success": true,
    "action": "turned_off",
    "message": "Light turned OFF per schedule"
}
```

## Future Enhancements

1. **Adjustable Polling Interval:** Allow user to configure check frequency
2. **Schedule Preview:** Show next ON/OFF time
3. **Multiple Schedules:** Support different schedules per day
4. **Sunrise/Sunset:** Automatically adjust based on location
5. **Notification:** Alert user when schedule executes
6. **History:** Log all schedule-triggered actions

