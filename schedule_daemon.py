#!/usr/bin/env python3
"""
Schedule Daemon for Light Relay Control
Monitors the light schedule and automatically toggles the RelayLight device
based on configured ON/OFF times.
"""
import os
import sys
import time
import logging
import sqlite3
import requests
from datetime import datetime, time as dt_time
from pathlib import Path

# Setup logging
LOG_DIR = Path("/var/log")
LOG_FILE = LOG_DIR / "jebi-schedule-daemon.log"

# Create log directory if it doesn't exist (for development)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL = 60  # Check every 60 seconds
DB_PATH = os.path.join(os.path.dirname(__file__), 'dev_users.db')
API_BASE_URL = "http://localhost:5000"  # Adjust if needed


class ScheduleDaemon:
    """Daemon to monitor and execute light schedules."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.last_state = None  # Track last relay state to avoid unnecessary toggles
        self.last_check_date = None  # Track date to detect day changes
        logger.info("Schedule Daemon initialized")
        logger.info(f"Database path: {self.db_path}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    
    def get_schedule(self):
        """Fetch schedule from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT device_id, start_time, end_time, days, enabled, created_at, updated_at
                FROM schedules
                WHERE device_id = 'RelayLight'
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                schedule = dict(row)
                # Parse days from comma-separated string to list
                if schedule['days']:
                    schedule['days'] = [d.strip() for d in schedule['days'].split(',')]
                else:
                    schedule['days'] = []
                return schedule
            return None
            
        except Exception as e:
            logger.error(f"Error fetching schedule from database: {e}")
            return None
    
    def is_today_scheduled(self, schedule_days):
        """Check if today is in the scheduled days."""
        if not schedule_days:
            return True  # If no days specified, run every day
        
        day_map = {
            0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu',
            4: 'fri', 5: 'sat', 6: 'sun'
        }
        
        today = datetime.now().weekday()
        today_abbr = day_map.get(today, '')
        
        return today_abbr in schedule_days
    
    def should_light_be_on(self, schedule):
        """Determine if light should be ON based on schedule and current time."""
        if not schedule or not schedule.get('enabled'):
            return False
        
        # Check if today is a scheduled day
        if not self.is_today_scheduled(schedule.get('days', [])):
            return False
        
        start_time_str = schedule.get('start_time')
        end_time_str = schedule.get('end_time')
        
        if not start_time_str or not end_time_str:
            logger.warning("Schedule has no start_time or end_time")
            return False
        
        # Parse times
        try:
            start_hour, start_min = map(int, start_time_str.split(':'))
            end_hour, end_min = map(int, end_time_str.split(':'))
            
            start_time = dt_time(start_hour, start_min)
            end_time = dt_time(end_hour, end_min)
            current_time = datetime.now().time()
            
            # Note: The database stores swapped times for overnight schedules
            # start_time < end_time always in DB
            # But we need to interpret based on the actual ON/OFF times
            
            # If start < end: normal daytime period (lights ON during this time)
            # If start > end: this shouldn't happen in DB due to our swap logic
            
            # The actual logic: if current time is between start and end
            if start_time <= end_time:
                # Normal schedule: ON between start and end
                return start_time <= current_time < end_time
            else:
                # This case shouldn't occur due to DB validation
                # But handle it anyway: overnight schedule
                return current_time >= start_time or current_time < end_time
                
        except Exception as e:
            logger.error(f"Error parsing schedule times: {e}")
            return False
    
    def toggle_relay(self, action):
        """Toggle the RelayLight via API."""
        try:
            url = f"{API_BASE_URL}/revpi-toggle"
            data = {
                'device': 'RelayLight',
                'action': action
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                logger.info(f"Successfully toggled RelayLight to {action.upper()}")
                return True
            else:
                logger.error(f"Failed to toggle RelayLight: {result.get('message')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error toggling relay: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error toggling relay: {e}")
            return False
    
    def check_and_update_relay(self):
        """Main logic to check schedule and update relay state."""
        try:
            # Get current schedule
            schedule = self.get_schedule()
            
            if not schedule:
                logger.debug("No schedule found for RelayLight")
                # If no schedule and light was on, turn it off
                if self.last_state == 'on':
                    logger.info("No schedule found, turning light OFF")
                    self.toggle_relay('off')
                    self.last_state = 'off'
                return
            
            # Check if schedule is enabled
            if not schedule.get('enabled'):
                logger.debug("Schedule exists but is disabled")
                # If schedule is disabled and light was on, turn it off
                if self.last_state == 'on':
                    logger.info("Schedule disabled, turning light OFF")
                    self.toggle_relay('off')
                    self.last_state = 'off'
                return
            
            # Determine desired state
            should_be_on = self.should_light_be_on(schedule)
            desired_state = 'on' if should_be_on else 'off'
            
            # Check for day change - force state update on new day
            current_date = datetime.now().date()
            if self.last_check_date != current_date:
                logger.info(f"Day changed to {current_date}, forcing state update")
                self.last_check_date = current_date
                # Force update by clearing last state
                self.last_state = None
            
            # Only toggle if state needs to change
            if self.last_state != desired_state:
                logger.info(f"State change detected: {self.last_state} -> {desired_state}")
                logger.info(f"Schedule: ON at {schedule['start_time']}, OFF at {schedule['end_time']}")
                logger.info(f"Days: {', '.join(schedule.get('days', ['all']))}")
                
                if self.toggle_relay(desired_state):
                    self.last_state = desired_state
                    
                    # Log activation to database
                    self.log_activation(desired_state)
            else:
                logger.debug(f"Relay state unchanged: {desired_state}")
                
        except Exception as e:
            logger.error(f"Error in check_and_update_relay: {e}", exc_info=True)
    
    def log_activation(self, action):
        """Log relay activation to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO relay_activations 
                (device_id, action, user_id, username, is_automatic, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'RelayLight',
                action,
                None,
                'schedule-daemon',
                1,  # is_automatic
                1,  # success
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.debug(f"Logged activation: RelayLight {action}")
            
        except Exception as e:
            logger.error(f"Error logging activation: {e}")
    
    def run(self):
        """Main daemon loop."""
        logger.info("Schedule Daemon starting...")
        logger.info(f"Monitoring RelayLight schedule every {CHECK_INTERVAL} seconds")
        
        while True:
            try:
                self.check_and_update_relay()
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Schedule Daemon stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                time.sleep(CHECK_INTERVAL)  # Continue after error


if __name__ == '__main__':
    daemon = ScheduleDaemon()
    daemon.run()
