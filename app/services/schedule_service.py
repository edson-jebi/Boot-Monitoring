"""
Schedule service for managing device schedules.
Refactored to use standardized error handling.
"""
import logging
from typing import Dict, Any
from app.models import Schedule
from app.utils import (
    ServiceResponse,
    ServiceException,
    ErrorCode,
    validate_required_params,
    validate_time_format
)

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service for managing device schedules with standardized error handling."""

    def __init__(self, config):
        """
        Initialize ScheduleService.

        Args:
            config: Application configuration object

        Raises:
            ServiceException: If initialization fails
        """
        try:
            self.config = config
            self.logger = logging.getLogger(__name__)
            self.logger.info("ScheduleService: config set successfully")

            # Create Schedule model instance
            self.schedule_model = Schedule()
            self.logger.info("ScheduleService: Schedule instance created successfully")

        except Exception as e:
            self.logger.error(f"ScheduleService initialization error: {e}", exc_info=True)
            raise ServiceException(
                message="Failed to initialize ScheduleService",
                error_code=ErrorCode.UNKNOWN_ERROR,
                details=str(e)
            )

    def save_schedule(
        self,
        device_id: str,
        start_time: str,
        end_time: str,
        days: list,
        enabled: bool = False,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Save a device schedule.

        Args:
            device_id: Device identifier
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            days: List of days (e.g., ['mon', 'tue', 'wed'])
            enabled: Whether schedule is enabled
            user_id: ID of user creating/updating schedule

        Returns:
            Standardized ServiceResponse dict with:
            - success: True if saved successfully
            - message: Human-readable message
            - data: Schedule details if successful
            - error_code: Error code if failed
        """
        try:
            # Validate required parameters
            validate_required_params(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                days=days if days else None  # Check for empty list
            )

            # Validate time formats
            validate_time_format(start_time, "start_time")
            validate_time_format(end_time, "end_time")

            # Validate that end time is after start time
            if start_time >= end_time:
                return ServiceResponse.error_response(
                    message='End time must be after start time',
                    error_code=ErrorCode.INVALID_DATE_RANGE.value,
                    details=f"start_time={start_time}, end_time={end_time}"
                ).to_dict()

            # Validate days
            valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            invalid_days = [day for day in days if day not in valid_days]

            if invalid_days:
                return ServiceResponse.error_response(
                    message='Invalid day(s) specified',
                    error_code=ErrorCode.VALIDATION_ERROR.value,
                    details=f"Invalid days: {invalid_days}. Valid days: {valid_days}"
                ).to_dict()

            if len(days) == 0:
                return ServiceResponse.error_response(
                    message='At least one day must be selected',
                    error_code=ErrorCode.VALIDATION_ERROR.value
                ).to_dict()

            # Save to database
            success = self.schedule_model.save_schedule(
                device_id, start_time, end_time, days, enabled, user_id
            )

            if success:
                self.logger.info(
                    f"Schedule saved for device '{device_id}': "
                    f"{start_time}-{end_time}, days: {days}, enabled: {enabled}"
                )
                return ServiceResponse.success_response(
                    message=f'Schedule saved for {device_id}',
                    data={
                        'device_id': device_id,
                        'start_time': start_time,
                        'end_time': end_time,
                        'days': days,
                        'enabled': enabled,
                        'user_id': user_id
                    }
                ).to_dict()
            else:
                self.logger.error(f"Failed to save schedule for device '{device_id}' to database")
                return ServiceResponse.error_response(
                    message='Failed to save schedule to database',
                    error_code=ErrorCode.DATABASE_ERROR.value,
                    details=f"Database operation failed for device '{device_id}'"
                ).to_dict()

        except ServiceException as e:
            self.logger.error(f"Validation error saving schedule for {device_id}: {e.message}")
            return e.to_response().to_dict()

        except Exception as e:
            self.logger.error(f"Unexpected error saving schedule for {device_id}: {e}", exc_info=True)
            return ServiceResponse.error_response(
                message='Internal error saving schedule',
                error_code=ErrorCode.UNKNOWN_ERROR.value,
                details=str(e)
            ).to_dict()

    def get_schedule(self, device_id: str) -> Dict[str, Any]:
        """
        Get schedule for a device.

        Args:
            device_id: Device identifier

        Returns:
            Standardized ServiceResponse dict
        """
        try:
            validate_required_params(device_id=device_id)

            schedule = self.schedule_model.get_schedule(device_id)

            if schedule:
                self.logger.info(f"Retrieved schedule for device '{device_id}'")
                return ServiceResponse.success_response(
                    message=f'Schedule retrieved for {device_id}',
                    data=schedule
                ).to_dict()
            else:
                self.logger.info(f"No schedule found for device '{device_id}'")
                return ServiceResponse.error_response(
                    message=f'No schedule found for device {device_id}',
                    error_code=ErrorCode.RECORD_NOT_FOUND.value
                ).to_dict()

        except ServiceException as e:
            return e.to_response().to_dict()

        except Exception as e:
            self.logger.error(f"Error getting schedule for {device_id}: {e}", exc_info=True)
            return ServiceResponse.error_response(
                message='Internal error getting schedule',
                error_code=ErrorCode.UNKNOWN_ERROR.value,
                details=str(e)
            ).to_dict()

    def get_all_schedules(self) -> Dict[str, Any]:
        """
        Get all device schedules.

        Returns:
            Standardized ServiceResponse dict with all schedules
        """
        try:
            schedules = self.schedule_model.get_all_schedules()

            self.logger.info(f"Retrieved {len(schedules)} schedule(s)")
            return ServiceResponse.success_response(
                message=f'Retrieved {len(schedules)} schedule(s)',
                data={'schedules': schedules}
            ).to_dict()

        except Exception as e:
            self.logger.error(f"Error getting all schedules: {e}", exc_info=True)
            return ServiceResponse.error_response(
                message='Internal error getting schedules',
                error_code=ErrorCode.UNKNOWN_ERROR.value,
                details=str(e)
            ).to_dict()

    def enable_schedule(self, device_id: str, enabled: bool = True) -> Dict[str, Any]:
        """
        Enable or disable a schedule.

        Args:
            device_id: Device identifier
            enabled: True to enable, False to disable

        Returns:
            Standardized ServiceResponse dict
        """
        try:
            validate_required_params(device_id=device_id)

            success = self.schedule_model.enable_schedule(device_id, enabled)

            if success:
                status = "enabled" if enabled else "disabled"
                self.logger.info(f"Schedule {status} for device '{device_id}'")
                return ServiceResponse.success_response(
                    message=f'Schedule {status} for {device_id}',
                    data={'device_id': device_id, 'enabled': enabled}
                ).to_dict()
            else:
                self.logger.warning(f"No schedule found for device '{device_id}' to enable/disable")
                return ServiceResponse.error_response(
                    message=f'No schedule found for device {device_id}',
                    error_code=ErrorCode.RECORD_NOT_FOUND.value
                ).to_dict()

        except ServiceException as e:
            return e.to_response().to_dict()

        except Exception as e:
            self.logger.error(f"Error enabling/disabling schedule for {device_id}: {e}", exc_info=True)
            return ServiceResponse.error_response(
                message='Internal error updating schedule',
                error_code=ErrorCode.UNKNOWN_ERROR.value,
                details=str(e)
            ).to_dict()

    def delete_schedule(self, device_id: str) -> Dict[str, Any]:
        """
        Delete a schedule.

        Args:
            device_id: Device identifier

        Returns:
            Standardized ServiceResponse dict
        """
        try:
            validate_required_params(device_id=device_id)

            success = self.schedule_model.delete_schedule(device_id)

            if success:
                self.logger.info(f"Schedule deleted for device '{device_id}'")
                return ServiceResponse.success_response(
                    message=f'Schedule deleted for {device_id}',
                    data={'device_id': device_id}
                ).to_dict()
            else:
                self.logger.warning(f"No schedule found for device '{device_id}' to delete")
                return ServiceResponse.error_response(
                    message=f'No schedule found for device {device_id}',
                    error_code=ErrorCode.RECORD_NOT_FOUND.value
                ).to_dict()

        except ServiceException as e:
            return e.to_response().to_dict()

        except Exception as e:
            self.logger.error(f"Error deleting schedule for {device_id}: {e}", exc_info=True)
            return ServiceResponse.error_response(
                message='Internal error deleting schedule',
                error_code=ErrorCode.UNKNOWN_ERROR.value,
                details=str(e)
            ).to_dict()
