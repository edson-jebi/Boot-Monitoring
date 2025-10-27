# Real-time Logs Implementation

## Overview
Implemented real-time log viewing functionality in the System Logs section of `bradken-switchos-mockup.html` using the existing log directory browser from `config_editor.html`. Logs automatically refresh every 10 seconds with a visible timestamp showing the last update time.

## Changes Made

### 1. Frontend Updates (`templates/bradken-switchos-mockup.html`)

#### Updated Logs Preview Section
- Replaced static log entries with dynamic container
- Removed manual refresh button
- Added "Last Updated" timestamp that shows when logs were last refreshed
- Changed title to "Recent Activity (Switchboard Guard)"

```html
<div class="logs-preview">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 class="logs-preview-title">Recent Activity (Switchboard Guard)</h3>
        <span id="logsLastUpdate">Updated at HH:MM:SS</span>
    </div>
    <div id="switchboardLogsContainer">
        <div class="log-line info">Loading logs...</div>
    </div>
</div>
```

#### Added JavaScript Functions

1. **`loadSwitchboardLogs()`**
   - Uses existing `/log-directory` endpoint from config_editor
   - Finds `check_alive_strict.log` file
   - Downloads and parses log content
   - Displays last 50 lines in reverse order (most recent first)
   - Updates the last refresh timestamp

2. **`updateLastRefreshTime(status)`**
   - Updates the "Last Updated" timestamp display
   - Shows current time when logs are refreshed
   - Adds subtle color flash animation on update
   - Displays error status if refresh fails

3. **`displaySwitchboardLogs(logContent)`**
   - Parses log file content line by line
   - Identifies log levels (INFO, WARNING, ERROR, CRITICAL)
   - Applies appropriate CSS classes for styling
   - Shows most recent 50 entries

4. **`startLogsAutoRefresh()` / `stopLogsAutoRefresh()`**
   - Auto-refresh logs every **10 seconds** when on logs screen (reduced from 30s)
   - Stops auto-refresh when navigating away

#### Updated Navigation Functions
- `navigateToLogs()`: Loads logs and starts auto-refresh
- `navigateToScreen()`: Stops auto-refresh when leaving logs screen

## Log File Details

**Path**: `/var/log/jebi-switchboard/check_alive_strict.log`

**Format**: `YYYY-MM-DD HH:MM:SS LEVEL source - message`

**Example**:
```
2025-10-27 22:02:26 CRITICAL check-guard - Max power cycles (4) reached
2025-10-27 22:02:17 INFO check-guard - POWER CYCLE COMPLETE
2025-10-27 22:02:07 ERROR check-guard - Triggering power cycle #4
```

## Log Level Styling

| Level    | CSS Class | Color  |
|----------|-----------|--------|
| INFO     | info      | Gray   |
| WARNING  | warn      | Yellow |
| ERROR    | error     | Red    |
| CRITICAL | error     | Red    |

## Features

1. ✅ **Real-time Updates**: Logs refresh automatically every 10 seconds
2. ✅ **Auto-Refresh**: No manual button needed - fully automatic
3. ✅ **Timestamp Display**: Shows "Updated at HH:MM:SS" with visual flash
4. ✅ **Recent First**: Shows most recent 50 log entries in reverse chronological order
5. ✅ **Color Coding**: Different colors for different log levels
6. ✅ **Reuses Existing Infrastructure**: Uses `/log-directory` and `/download-log-file` endpoints
7. ✅ **Error Handling**: Graceful error messages if logs unavailable
8. ✅ **Visual Feedback**: Timestamp changes color briefly when logs update

## User Experience

- **Automatic**: Logs load immediately when navigating to Logs page
- **Seamless**: Updates happen in background every 10 seconds
- **Informative**: Timestamp shows when last update occurred
- **Efficient**: Auto-refresh stops when user leaves the logs page

## Testing

To test the implementation:

1. Navigate to the System Logs page in the web interface
2. Logs automatically load from `/var/log/jebi-switchboard/check_alive_strict.log`
3. Watch the "Updated at" timestamp in the top right
4. Logs will auto-refresh every 10 seconds
5. Timestamp will briefly flash blue when logs update
6. Auto-refresh stops when navigating away from logs page

## Technical Details

- **Refresh Interval**: 10 seconds (configurable in `startLogsAutoRefresh()`)
- **Display Limit**: Last 50 log entries
- **Order**: Most recent first (reversed)
- **Timestamp Format**: Uses browser's `toLocaleTimeString()`
- **Visual Feedback**: 500ms color animation on timestamp update

## Dependencies

- Existing `/log-directory` endpoint (from config_editor)
- Existing `/download-log-file/<filename>` endpoint
- Log file must exist at `/var/log/jebi-switchboard/check_alive_strict.log`
- Log file must be readable by the web application user

## Notes

- No backend changes required - reuses existing endpoints
- Log parsing handles standard format from jebi-switchboard-guard service
- Performance: Only last 50 lines displayed to keep UI responsive
- Auto-refresh interval: 10 seconds (changed from 30s for more real-time feel)
- No manual refresh button - fully automatic experience
