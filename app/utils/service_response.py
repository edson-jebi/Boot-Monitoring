"""
Standardized response and error handling utilities for services.

This module provides consistent response structures across all services
to ensure uniform error handling and API responses.
"""
import logging
from typing import Any, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict


class ResponseStatus(Enum):
    """Standard response status codes."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ServiceResponse:
    """
    Standardized service response structure.

    All services should return this structure for consistency.

    Attributes:
        success: True if operation succeeded, False otherwise
        message: Human-readable message describing the result
        data: Optional additional data (dict, list, etc.)
        error_code: Optional error code for programmatic handling
        details: Optional detailed error information for debugging
    """
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, omitting None values."""
        result = {
            'success': self.success,
            'message': self.message
        }

        if self.data is not None:
            result['data'] = self.data

        if self.error_code is not None:
            result['error_code'] = self.error_code

        if self.details is not None:
            result['details'] = self.details

        return result

    @classmethod
    def success_response(
        cls,
        message: str,
        data: Optional[Any] = None
    ) -> 'ServiceResponse':
        """Create a success response."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(
        cls,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[str] = None
    ) -> 'ServiceResponse':
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            details=details
        )


class ErrorCode(Enum):
    """Standard error codes for service operations."""
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_PARAMETER = "MISSING_PARAMETER"

    # Device errors
    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    DEVICE_COMMUNICATION_ERROR = "DEVICE_COMMUNICATION_ERROR"
    DEVICE_TIMEOUT = "DEVICE_TIMEOUT"

    # Command errors
    COMMAND_FAILED = "COMMAND_FAILED"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    COMMAND_NOT_FOUND = "COMMAND_NOT_FOUND"

    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_TIME_FORMAT = "INVALID_TIME_FORMAT"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"

    # Service errors
    SERVICE_NOT_FOUND = "SERVICE_NOT_FOUND"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_ACTION_FAILED = "SERVICE_ACTION_FAILED"

    # Authentication/Authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"


class ServiceException(Exception):
    """
    Base exception for service layer errors.

    All service methods can raise this exception for exceptional cases
    that cannot be handled within the service layer.
    """
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

    def to_response(self) -> ServiceResponse:
        """Convert exception to ServiceResponse."""
        return ServiceResponse.error_response(
            message=self.message,
            error_code=self.error_code.value,
            details=self.details
        )


def handle_service_errors(logger: Optional[logging.Logger] = None):
    """
    Decorator to standardize error handling in service methods.

    Catches exceptions and converts them to ServiceResponse objects.
    Logs errors using the provided logger.

    Usage:
        @handle_service_errors(logger)
        def my_service_method(self, param):
            # Method implementation
            return ServiceResponse.success_response("Operation completed")
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # If already a ServiceResponse, return as-is
                if isinstance(result, ServiceResponse):
                    return result.to_dict()

                # If it's a dict with 'success' key, assume it's already formatted
                if isinstance(result, dict) and 'success' in result:
                    return result

                # Otherwise wrap in success response
                return ServiceResponse.success_response(
                    message="Operation completed successfully",
                    data=result
                ).to_dict()

            except ServiceException as e:
                logger.error(f"{func.__name__} failed: {e.message}", exc_info=True)
                return e.to_response().to_dict()

            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                return ServiceResponse.error_response(
                    message=f"Unexpected error: {str(e)}",
                    error_code=ErrorCode.UNKNOWN_ERROR.value,
                    details=str(e)
                ).to_dict()

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def validate_required_params(**params: Any) -> None:
    """
    Validate that required parameters are present and not None.

    Raises ServiceException if any parameter is missing or None.

    Usage:
        validate_required_params(
            device_id=device_id,
            action=action
        )
    """
    missing = [name for name, value in params.items() if value is None or value == '']

    if missing:
        raise ServiceException(
            message=f"Missing required parameters: {', '.join(missing)}",
            error_code=ErrorCode.MISSING_PARAMETER,
            details=f"The following parameters are required but missing: {missing}"
        )


def validate_time_format(time_str: str, param_name: str = "time") -> bool:
    """
    Validate time format (HH:MM).

    Args:
        time_str: Time string to validate
        param_name: Parameter name for error messages

    Returns:
        True if valid

    Raises:
        ServiceException if time format is invalid
    """
    try:
        if not time_str or not isinstance(time_str, str):
            raise ServiceException(
                message=f"Invalid {param_name}: must be a non-empty string",
                error_code=ErrorCode.INVALID_TIME_FORMAT
            )

        parts = time_str.split(':')
        if len(parts) != 2:
            raise ServiceException(
                message=f"Invalid {param_name} format: expected HH:MM",
                error_code=ErrorCode.INVALID_TIME_FORMAT,
                details=f"Received: {time_str}"
            )

        hour, minute = int(parts[0]), int(parts[1])

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ServiceException(
                message=f"Invalid {param_name}: hour must be 0-23, minute must be 0-59",
                error_code=ErrorCode.INVALID_TIME_FORMAT,
                details=f"Received: {time_str} (hour={hour}, minute={minute})"
            )

        return True

    except ValueError as e:
        raise ServiceException(
            message=f"Invalid {param_name} format: must be numeric HH:MM",
            error_code=ErrorCode.INVALID_TIME_FORMAT,
            details=f"Received: {time_str}, Error: {str(e)}"
        )


def create_logger(name: str) -> logging.Logger:
    """
    Create a standardized logger for service classes.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
