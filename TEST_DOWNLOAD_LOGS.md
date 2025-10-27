# Test Download Logs Feature

## **✅ FIXED - Ready to Test!**

The download feature is now fully functional. The issue was that the route wasn't registered in `/app/routes/main.py`.

## Changes Made

### 1. Backend (revpi_controller.py)
- ✅ Added `download_logs_by_date()` method
- ✅ Added debug logging to track requests

### 2. Route Registration (app/routes/main.py)  
- ✅ **FIXED**: Added route to main_bp: `/download-logs-by-date` (POST)

### 3. Frontend (bradken-switchos-mockup.html)
- ✅ Added ID `downloadLogsBtn` and class `download-logs-btn` to button
- ✅ Updated `downloadLogs()` function to use `getElementById`
- ✅ Added error checking for button not found
- ✅ Implemented date validation
- ✅ Added AJAX POST request with fetch API
- ✅ Handles blob response and triggers download

### 4. Server
- ✅ Restarted Gunicorn on port 5000
- ✅ 3 worker processes running
- ✅ Route is now accessible (tested with curl)

## How to Test

1. **Navigate to System Logs section** in the web interface
   - URL: `http://192.168.1.121:5000/bradken-switchos-mockup.html`
   - Look for the "System Logs" heading

2. **Select Date Range**:
   - From Date: Select a date (e.g., 2025-10-20)
   - To Date: Select today's date (2025-10-27)

3. **Click "Download Logs" button**:
   - Should show confirmation dialog with selected dates
   - Click "Download" in the dialog

4. **Expected Behavior**:
   - Button shows spinner: "Preparing Download..."
   - Browser downloads a ZIP file named: `jebi-switchboard-logs_2025-10-20_to_2025-10-27.zip`
   - Alert appears if no files found in date range

## Troubleshooting

### If download doesn't work:

1. **Check Browser Console** (F12):
   - Look for JavaScript errors
   - Check Network tab for the POST request to `/download-logs-by-date`
   - Verify response status (should be 200 for success)

2. **Check Server Logs**:
   ```bash
   tail -20 /home/pi/Boot-Monitoring/logs/jebi_web.log
   ```
   - Look for: "Received download request with data:"
   - Check for any error messages

3. **Verify log files exist**:
   ```bash
   ls -lh /var/log/jebi-switchboard/
   ```
   - Check modification dates of files
   - Ensure files were modified within your selected date range

4. **Test the endpoint directly** (from terminal):
   ```bash
   curl -X POST http://localhost:5000/download-logs-by-date \
     -H "Content-Type: application/json" \
     -d '{"from_date":"2025-10-20","to_date":"2025-10-27"}' \
     -o test-download.zip
   ```

## Common Issues

### Issue: "Please select both from and to dates"
**Solution**: Make sure both date fields are filled before clicking Download

### Issue: "No log files found between X and Y"
**Solution**: 
- Check if log files exist in `/var/log/jebi-switchboard/`
- Verify the files were modified within your selected date range
- Try a wider date range

### Issue: Button doesn't show spinner
**Solution**: 
- Check browser console for JavaScript errors
- Verify the button has ID `downloadLogsBtn`
- Refresh the page (Ctrl+F5)

### Issue: Error in server logs about permissions
**Solution**:
```bash
# Check permissions on log directory
ls -ld /var/log/jebi-switchboard/
# Should be readable by the pi user
```

## Debug Commands

```bash
# View recent log activity
tail -f /home/pi/Boot-Monitoring/logs/jebi_web.log | grep -i download

# Check if endpoint is registered
curl -X OPTIONS http://localhost:5000/download-logs-by-date -v

# List log files with modification times
ls -lt /var/log/jebi-switchboard/ | head -20

# Count log files
ls -1 /var/log/jebi-switchboard/ | wc -l
```

## Success Indicators

When working correctly, you should see:
1. ✅ Confirmation dialog appears with your selected dates
2. ✅ Button changes to show spinner and "Preparing Download..."
3. ✅ In logs: "Received download request with data: {'from_date': ..., 'to_date': ...}"
4. ✅ In logs: "User 'bradken' performed action: downloaded logs"
5. ✅ Browser downloads a ZIP file
6. ✅ Button returns to normal "Download Logs" text
