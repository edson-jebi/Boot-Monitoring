"""
Input validation utilities for JEBI Web Application.
Provides validation functions to prevent injection attacks and ensure data integrity.
"""
import re
from typing import Optional, List, Tuple
from config import config_map_revpi


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Centralized input validation for the application."""

    # Valid device IDs from configuration
    VALID_DEVICES = set(config_map_revpi.keys())

    # Valid systemd service names (whitelist pattern)
    VALID_SERVICE_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+\.service$')
    ALLOWED_SERVICES = {
        'jebi-switchboard-guard.service',
        'jebi-switchboard.service'
    }

    # Valid actions for device control
    VALID_DEVICE_ACTIONS = {'on', 'off', 'status'}

    # Valid service control actions
    VALID_SERVICE_ACTIONS = {'start', 'stop', 'restart', 'status'}

    # Valid days of week for scheduling
    VALID_DAYS = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}

    # Valid time format (HH:MM)
    TIME_PATTERN = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')

    # Path traversal patterns to block
    PATH_TRAVERSAL_PATTERNS = ['..', '/', '\\', '\x00']

    @classmethod
    def validate_device_id(cls, device_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate device ID against whitelist.

        Args:
            device_id: Device identifier to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not device_id:
            return False, "Device ID cannot be empty"

        if not isinstance(device_id, str):
            return False, "Device ID must be a string"

        if device_id not in cls.VALID_DEVICES:
            return False, f"Invalid device ID. Must be one of: {', '.join(cls.VALID_DEVICES)}"

        return True, None

    @classmethod
    def validate_service_name(cls, service_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate systemd service name against whitelist and pattern.

        Args:
            service_name: Service name to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not service_name:
            return False, "Service name cannot be empty"

        if not isinstance(service_name, str):
            return False, "Service name must be a string"

        # Check whitelist first
        if service_name in cls.ALLOWED_SERVICES:
            return True, None

        # Check against pattern
        if not cls.VALID_SERVICE_PATTERN.match(service_name):
            return False, "Invalid service name format. Must end with .service"

        return False, f"Service not allowed. Must be one of: {', '.join(cls.ALLOWED_SERVICES)}"

    @classmethod
    def validate_device_action(cls, action: str) -> Tuple[bool, Optional[str]]:
        """
        Validate device control action.

        Args:
            action: Action to validate (on/off/status)

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not action:
            return False, "Action cannot be empty"

        if not isinstance(action, str):
            return False, "Action must be a string"

        action_lower = action.lower()
        if action_lower not in cls.VALID_DEVICE_ACTIONS:
            return False, f"Invalid action. Must be one of: {', '.join(cls.VALID_DEVICE_ACTIONS)}"

        return True, None

    @classmethod
    def validate_service_action(cls, action: str) -> Tuple[bool, Optional[str]]:
        """
        Validate service control action.

        Args:
            action: Action to validate (start/stop/restart/status)

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not action:
            return False, "Action cannot be empty"

        if not isinstance(action, str):
            return False, "Action must be a string"

        action_lower = action.lower()
        if action_lower not in cls.VALID_SERVICE_ACTIONS:
            return False, f"Invalid action. Must be one of: {', '.join(cls.VALID_SERVICE_ACTIONS)}"

        return True, None

    @classmethod
    def validate_schedule_days(cls, days: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate schedule days.

        Args:
            days: List of day abbreviations (mon, tue, etc.)

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not days:
            return False, "At least one day must be specified"

        if not isinstance(days, list):
            return False, "Days must be a list"

        invalid_days = [day for day in days if day.lower() not in cls.VALID_DAYS]
        if invalid_days:
            return False, f"Invalid days: {', '.join(invalid_days)}. Must be: {', '.join(cls.VALID_DAYS)}"

        return True, None

    @classmethod
    def validate_time(cls, time_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate time string format (HH:MM).

        Args:
            time_str: Time string to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not time_str:
            return False, "Time cannot be empty"

        if not isinstance(time_str, str):
            return False, "Time must be a string"

        if not cls.TIME_PATTERN.match(time_str):
            return False, "Invalid time format. Must be HH:MM (24-hour format)"

        return True, None

    @classmethod
    def validate_filename(cls, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate filename to prevent path traversal attacks.

        Args:
            filename: Filename to validate

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"

        if not isinstance(filename, str):
            return False, "Filename must be a string"

        # Check for path traversal patterns
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if pattern in filename:
                return False, f"Filename contains invalid characters: {pattern}"

        # Additional check: filename should not start with special characters
        if filename.startswith(('.', '-', '_')):
            return False, "Filename cannot start with special characters"

        # Check for reasonable length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"

        return True, None

    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize a string by removing potentially dangerous characters.

        Args:
            input_str: String to sanitize
            max_length: Maximum allowed length

        Returns:
            str: Sanitized string
        """
        if not isinstance(input_str, str):
            return ""

        # Remove null bytes and control characters
        sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\r\t')

        # Truncate to max length
        return sanitized[:max_length]


# Convenience functions for direct use
def validate_device_id(device_id: str) -> None:
    """
    Validate device ID and raise ValidationError if invalid.

    Args:
        device_id: Device identifier to validate

    Raises:
        ValidationError: If device_id is invalid
    """
    is_valid, error_msg = InputValidator.validate_device_id(device_id)
    if not is_valid:
        raise ValidationError(error_msg)


def validate_service_name(service_name: str) -> None:
    """
    Validate service name and raise ValidationError if invalid.

    Args:
        service_name: Service name to validate

    Raises:
        ValidationError: If service_name is invalid
    """
    is_valid, error_msg = InputValidator.validate_service_name(service_name)
    if not is_valid:
        raise ValidationError(error_msg)


def validate_device_action(action: str) -> None:
    """
    Validate device action and raise ValidationError if invalid.

    Args:
        action: Action to validate

    Raises:
        ValidationError: If action is invalid
    """
    is_valid, error_msg = InputValidator.validate_device_action(action)
    if not is_valid:
        raise ValidationError(error_msg)


def validate_service_action(action: str) -> None:
    """
    Validate service action and raise ValidationError if invalid.

    Args:
        action: Action to validate

    Raises:
        ValidationError: If action is invalid
    """
    is_valid, error_msg = InputValidator.validate_service_action(action)
    if not is_valid:
        raise ValidationError(error_msg)


def validate_filename(filename: str) -> None:
    """
    Validate filename and raise ValidationError if invalid.

    Args:
        filename: Filename to validate

    Raises:
        ValidationError: If filename is invalid
    """
    is_valid, error_msg = InputValidator.validate_filename(filename)
    if not is_valid:
        raise ValidationError(error_msg)


__all__ = [
    'InputValidator',
    'ValidationError',
    'validate_device_id',
    'validate_service_name',
    'validate_device_action',
    'validate_service_action',
    'validate_filename'
]
