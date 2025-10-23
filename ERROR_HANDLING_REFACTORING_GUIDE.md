# Error Handling Refactoring Guide

## Overview

This guide explains how to refactor services to use the new standardized error handling system.

## Problem Statement

Our services currently have **4 different error response patterns**:
- Pattern A: `{'success': bool, 'message': str}`
- Pattern B: `{'success': bool, 'error': str}`
- Pattern C: `{'status': str, ...}`
- Pattern D: `{'success': bool, 'message': str, 'error': str, 'output': str}`

This inconsistency makes it difficult to:
- Handle errors uniformly in controllers
- Write tests
- Debug issues
- Maintain code

## Solution: Standardized Response Structure

All services now return:
```python
{
    'success': bool,           # True if operation succeeded
    'message': str,            # Human-readable message
    'data': Any,              # Optional: result data
    'error_code': str,        # Optional: programmatic error code
    'details': str            # Optional: debug information
}
```

## New Utilities

### 1. ServiceResponse Class

```python
from app.utils import ServiceResponse

# Success response
return ServiceResponse.success_response(
    message="Device toggled successfully",
    data={'device_id': 'LedProcessor', 'state': 'on'}
).to_dict()

# Error response
return ServiceResponse.error_response(
    message="Device not found",
    error_code=ErrorCode.DEVICE_NOT_FOUND.value,
    details=f"Device '{device_id}' is not in device map"
).to_dict()
```

### 2. ServiceException Class

```python
from app.utils import ServiceException, ErrorCode

# Raise for exceptional cases
if device_id not in self.device_map:
    raise ServiceException(
        message="Invalid device ID",
        error_code=ErrorCode.DEVICE_NOT_FOUND,
        details=f"Device '{device_id}' not found in configuration"
    )
```

### 3. Validation Helpers

```python
from app.utils import validate_required_params, validate_time_format

# Validate required parameters
validate_required_params(
    device_id=device_id,
    action=action
)

# Validate time format
validate_time_format(start_time, "start_time")
validate_time_format(end_time, "end_time")
```

### 4. Error Handling Decorator

```python
from app.utils import handle_service_errors

class MyService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @handle_service_errors(logger)
    def my_method(self, param):
        # Your code here
        # Exceptions are automatically caught and converted to ServiceResponse
        return ServiceResponse.success_response("Success!")
```

## Refactoring Steps

### Step 1: Add Logger to Service Class

**Before:**
```python
class SystemdService:
    def __init__(self, config):
        self.config = config
```

**After:**
```python
import logging

class SystemdService:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
```

### Step 2: Import New Utilities

```python
from app.utils import (
    ServiceResponse,
    ServiceException,
    ErrorCode,
    validate_required_params
)
```

### Step 3: Refactor Return Statements

**Before (Pattern A):**
```python
return {
    'success': False,
    'message': 'Device not found'
}
```

**After:**
```python
return ServiceResponse.error_response(
    message='Device not found',
    error_code=ErrorCode.DEVICE_NOT_FOUND.value
).to_dict()
```

**Before (Pattern B):**
```python
return {
    'success': False,
    'error': 'Command failed'
}
```

**After:**
```python
return ServiceResponse.error_response(
    message='Command failed',
    error_code=ErrorCode.COMMAND_FAILED.value
).to_dict()
```

**Before (Pattern C - Status-based):**
```python
return {
    'status': DeviceStatus.ERROR.value,
    'error': 'Device unavailable'
}
```

**After:**
```python
# For status queries, include status in data
return ServiceResponse.error_response(
    message='Device unavailable',
    error_code=ErrorCode.DEVICE_UNAVAILABLE.value
).to_dict()

# OR for backward compatibility:
return ServiceResponse.success_response(
    message='Device status retrieved',
    data={
        'status': DeviceStatus.ERROR.value,
        'reason': 'Device unavailable'
    }
).to_dict()
```

### Step 4: Replace Validation Code

**Before:**
```python
if not device_id or not action:
    return {'success': False, 'message': 'Missing device or action'}
```

**After:**
```python
try:
    validate_required_params(device_id=device_id, action=action)
except ServiceException as e:
    return e.to_response().to_dict()
```

### Step 5: Standardize Exception Handling

**Before:**
```python
try:
    result = some_operation()
    return {'success': True, 'output': result}
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {'success': False, 'error': str(e)}
```

**After:**
```python
try:
    result = some_operation()
    return ServiceResponse.success_response(
        message="Operation completed",
        data={'output': result}
    ).to_dict()
except Exception as e:
    self.logger.error(f"Operation failed: {e}", exc_info=True)
    return ServiceResponse.error_response(
        message="Operation failed",
        error_code=ErrorCode.UNKNOWN_ERROR.value,
        details=str(e)
    ).to_dict()
```

### Step 6: Remove Debug Print Statements

**Before:**
```python
print(first_line)  # Debug
print("tem,ptemp")  # Debug
```

**After:**
```python
self.logger.debug(f"First line: {first_line}")
self.logger.debug("Processing temperature data")
```

## Controller Changes

Controllers should handle the standardized response:

**Before:**
```python
result = service.do_something()
if result.get('success'):
    return jsonify(result)
else:
    return jsonify(result), 500
```

**After:**
```python
result = service.do_something()
if result['success']:
    return jsonify(result)
else:
    # Optionally map error codes to HTTP status codes
    status_code = get_http_status_for_error(result.get('error_code'))
    return jsonify(result), status_code
```

## Error Code to HTTP Status Mapping

```python
def get_http_status_for_error(error_code: str) -> int:
    """Map error codes to HTTP status codes."""
    mapping = {
        'INVALID_INPUT': 400,
        'MISSING_PARAMETER': 400,
        'VALIDATION_ERROR': 400,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'DEVICE_NOT_FOUND': 404,
        'RECORD_NOT_FOUND': 404,
        'DEVICE_TIMEOUT': 408,
        'COMMAND_TIMEOUT': 408,
        'DUPLICATE_ENTRY': 409,
        'DEVICE_UNAVAILABLE': 503,
        'SERVICE_UNAVAILABLE': 503,
    }
    return mapping.get(error_code, 500)
```

## Testing

### Unit Test Example

```python
def test_device_toggle_success(self):
    service = RevPiService(config, device_map)
    result = service.toggle_device('LedProcessor', DeviceAction.ON)

    assert result['success'] == True
    assert 'message' in result
    assert result['data']['device_id'] == 'LedProcessor'

def test_device_toggle_not_found(self):
    service = RevPiService(config, device_map)
    result = service.toggle_device('InvalidDevice', DeviceAction.ON)

    assert result['success'] == False
    assert result['error_code'] == 'DEVICE_NOT_FOUND'
    assert 'message' in result
```

## Migration Checklist

For each service file:

- [ ] Add `self.logger = logging.getLogger(__name__)`
- [ ] Import new utilities from `app.utils`
- [ ] Replace all `print()` with `self.logger.debug()` or `self.logger.info()`
- [ ] Convert all return statements to use `ServiceResponse`
- [ ] Replace custom validation with `validate_required_params()` and `validate_time_format()`
- [ ] Use consistent error codes from `ErrorCode` enum
- [ ] Update error logging to use `exc_info=True`
- [ ] Update docstrings to reflect new return format
- [ ] Update unit tests
- [ ] Update controller error handling

## Benefits

1. **Consistency**: All services return the same structure
2. **Type Safety**: Using classes instead of raw dicts
3. **Better Errors**: Programmatic error codes + human messages
4. **Easier Testing**: Predictable response structure
5. **Better Logging**: Standardized logging patterns
6. **Maintainability**: Clear separation of concerns
7. **Documentation**: Self-documenting error codes

## Questions?

- Check examples in refactored services
- Review `app/utils/service_response.py` for full API
- Look at unit tests for usage patterns
