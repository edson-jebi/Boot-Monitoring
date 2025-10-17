"""
Schedule service for managing device schedules.
"""
import logging
from typing import Dict, Any, Optional
from app.models import Schedule

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for managing device schedules."""
    
    def __init__(self, config):
        try:
            self.config = config
            logger.info("ScheduleService: config set successfully")
            
            # Create Schedule instance
            self.schedule_model = Schedule()
            logger.info("ScheduleService: Schedule instance created successfully")
            
        except Exception as e:
            logger.error(f"ScheduleService initialization error: {e}")
            import traceback
            logger.error(f"ScheduleService traceback: {traceback.format_exc()}")
            raise
    
    def save_schedule(self, device_id: str, start_time: str, end_time: str, 
                     days: list, enabled: bool = False, user_id: int = None) -> Dict[str, Any]:
        """Save a device schedule."""
        try:
            # Validate input
            if not device_id or not start_time or not end_time or not days:
                return {
                    'success': False,
                    'message': 'Missing required schedule parameters'
                }
            
            # Validate time format (basic check)
            if not self._validate_time_format(start_time) or not self._validate_time_format(end_time):
                return {
                    'success': False,
                    'message': 'Invalid time format. Use HH:MM format'
                }
            
            # Validate that end time is after start time
            if start_time >= end_time:
                return {
                    'success': False,
                    'message': 'End time must be after start time'
                }
            
            # Validate days
            valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            if not all(day in valid_days for day in days):
                return {
                    'success': False,
                    'message': 'Invalid day specified'
                }
            
            if len(days) == 0:
                return {
                    'success': False,
                    'message': 'At least one day must be selected'
                }
            
            # Save to database
            success = self.schedule_model.save_schedule(
                device_id, start_time, end_time, days, enabled, user_id
            )
            
            if success:
                return {
                    'success': True,
                    'message': f'Schedule saved for {device_id}',
                    'schedule': {
                        'device_id': device_id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'days': days,
                        'enabled': enabled
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to save schedule to database'
                }
                
        except Exception as e:
            logger.error(f"Error saving schedule for {device_id}: {e}")
            return {
                'success': False,
                'message': 'Internal error saving schedule'
            }
    
    def get_schedule(self, device_id: str) -> Dict[str, Any]:
        """Get schedule for a device."""
        try:
            schedule = self.schedule_model.get_schedule(device_id)
            
            if schedule:
                return {
                    'success': True,
                    'schedule': schedule
                }
            else:
                return {
                    'success': False,
                    'message': f'No schedule found for device {device_id}'
                }
                
        except Exception as e:
            logger.error(f"Error getting schedule for {device_id}: {e}")
            return {
                'success': False,
                'message': 'Internal error getting schedule'
            }
    
    def get_all_schedules(self) -> Dict[str, Any]:
        """Get all device schedules."""
        try:
            schedules = self.schedule_model.get_all_schedules()
            return {
                'success': True,
                'schedules': schedules
            }
            
        except Exception as e:
            logger.error(f"Error getting all schedules: {e}")
            return {
                'success': False,
                'message': 'Internal error getting schedules'
            }
    
    def enable_schedule(self, device_id: str, enabled: bool = True) -> Dict[str, Any]:
        """Enable or disable a schedule."""
        try:
            success = self.schedule_model.enable_schedule(device_id, enabled)
            
            if success:
                status = "enabled" if enabled else "disabled"
                return {
                    'success': True,
                    'message': f'Schedule {status} for {device_id}'
                }
            else:
                return {
                    'success': False,
                    'message': f'No schedule found for device {device_id}'
                }
                
        except Exception as e:
            logger.error(f"Error enabling/disabling schedule for {device_id}: {e}")
            return {
                'success': False,
                'message': 'Internal error updating schedule'
            }
    
    def delete_schedule(self, device_id: str) -> Dict[str, Any]:
        """Delete a schedule."""
        try:
            success = self.schedule_model.delete_schedule(device_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Schedule deleted for {device_id}'
                }
            else:
                return {
                    'success': False,
                    'message': f'No schedule found for device {device_id}'
                }
                
        except Exception as e:
            logger.error(f"Error deleting schedule for {device_id}: {e}")
            return {
                'success': False,
                'message': 'Internal error deleting schedule'
            }
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format HH:MM."""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
            
        except (ValueError, AttributeError):
            return False
