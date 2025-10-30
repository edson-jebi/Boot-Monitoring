"""
Configuration validator for JEBI Web Application.
Validates environment variables and application configuration at startup.
"""
import os
import logging
from typing import Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_application_config() -> Tuple[bool, List[str], List[str]]:
    """
    Validate application configuration and environment.

    Returns:
        Tuple containing:
        - is_valid (bool): True if configuration is valid
        - errors (List[str]): List of critical errors
        - warnings (List[str]): List of warnings
    """
    errors = []
    warnings = []

    # Get environment
    flask_env = os.environ.get('FLASK_ENV', 'development')

    # Validate SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if flask_env == 'production':
            errors.append("SECRET_KEY environment variable must be set in production")
        else:
            warnings.append("SECRET_KEY not set - using default (not secure for production)")
    elif secret_key == 'dev-key-change-in-production':
        if flask_env == 'production':
            errors.append("SECRET_KEY is still set to default value in production")
        else:
            warnings.append("Using default SECRET_KEY (change for production)")
    elif len(secret_key) < 32:
        warnings.append(f"SECRET_KEY is short ({len(secret_key)} chars) - recommend at least 32 characters")

    # Validate DEBUG mode
    debug = os.environ.get('DEBUG', 'False').lower()
    if flask_env == 'production' and debug == 'true':
        errors.append("DEBUG mode is enabled in production environment")

    # Validate PORT
    port = os.environ.get('PORT', '5000')
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            errors.append(f"PORT must be between 1 and 65535 (current: {port_num})")
        elif port_num < 1024 and flask_env == 'production':
            warnings.append(f"PORT {port_num} is privileged - may require root access")
    except ValueError:
        errors.append(f"PORT must be a valid integer (current: {port})")

    # Validate DATABASE_PATH
    db_path = os.environ.get('DATABASE_PATH', 'users.db')
    db_file = Path(db_path)

    # Check if database directory exists and is writable
    if db_file.is_absolute():
        db_dir = db_file.parent
        if not db_dir.exists():
            warnings.append(f"Database directory does not exist: {db_dir}")
        elif not os.access(db_dir, os.W_OK):
            errors.append(f"Database directory is not writable: {db_dir}")

    # Validate SESSION_TIMEOUT
    session_timeout = os.environ.get('SESSION_TIMEOUT', '3600')
    try:
        timeout = int(session_timeout)
        if timeout < 60:
            warnings.append(f"SESSION_TIMEOUT is very short ({timeout}s) - users may be logged out frequently")
        elif timeout > 86400:
            warnings.append(f"SESSION_TIMEOUT is very long ({timeout}s) - may be a security risk")
    except ValueError:
        errors.append(f"SESSION_TIMEOUT must be a valid integer (current: {session_timeout})")

    # Validate COMMAND_TIMEOUT
    command_timeout = os.environ.get('COMMAND_TIMEOUT', '10')
    try:
        timeout = int(command_timeout)
        if timeout < 1:
            errors.append(f"COMMAND_TIMEOUT must be positive (current: {timeout})")
        elif timeout > 60:
            warnings.append(f"COMMAND_TIMEOUT is long ({timeout}s) - commands may block application")
    except ValueError:
        errors.append(f"COMMAND_TIMEOUT must be a valid integer (current: {command_timeout})")

    # Validate APP_BRAND
    app_brand = os.environ.get('APP_BRAND', 'BRADKEN')
    valid_brands = ['BRADKEN', 'JEBI']
    if app_brand not in valid_brands:
        warnings.append(f"APP_BRAND '{app_brand}' is not standard - expected one of: {', '.join(valid_brands)}")

    # Validate default credentials
    default_username = os.environ.get('DEFAULT_USERNAME', 'bradken')
    default_password = os.environ.get('DEFAULT_PASSWORD', 'adminBradken25')

    if not default_username:
        errors.append("DEFAULT_USERNAME cannot be empty")
    elif len(default_username) < 3:
        warnings.append(f"DEFAULT_USERNAME is short ({len(default_username)} chars)")

    if not default_password:
        errors.append("DEFAULT_PASSWORD cannot be empty")
    elif len(default_password) < 8:
        warnings.append(f"DEFAULT_PASSWORD is weak (less than 8 characters)")
    elif default_password in ['admin', 'password', 'adminBradken25', 'adminJEBI25']:
        if flask_env == 'production':
            errors.append("DEFAULT_PASSWORD is using a common/default password in production")
        else:
            warnings.append("DEFAULT_PASSWORD is common - change for production")

    # Check for production-specific configurations
    if flask_env == 'production':
        # Warn if using SQLite in production
        if db_path.endswith('.db') or ':memory:' in db_path:
            warnings.append("Using SQLite in production - consider PostgreSQL/MySQL for better performance")

        # Check if running as root
        if os.geteuid() == 0:
            warnings.append("Running as root user - recommend using a dedicated service account")

    # Check RevPi configuration files
    device_map_path = os.environ.get('DEVICE_MAP_PATH', '/home/pi/jebi-switchboard/config/strict_log_config.json')
    if device_map_path:
        if not Path(device_map_path).exists():
            warnings.append(f"Device map configuration file not found: {device_map_path}")

    log_path = os.environ.get('LOG_PATH', '/var/log/jebi-switchboard')
    if log_path:
        log_dir = Path(log_path)
        if not log_dir.exists():
            warnings.append(f"Log directory does not exist: {log_path}")
        elif not os.access(log_dir, os.R_OK):
            warnings.append(f"Log directory is not readable: {log_path}")

    # Determine if configuration is valid
    is_valid = len(errors) == 0

    # Log summary
    if is_valid:
        if warnings:
            logger.info(f"Configuration validation passed with {len(warnings)} warning(s)")
        else:
            logger.info("Configuration validation passed successfully")
    else:
        logger.error(f"Configuration validation failed with {len(errors)} error(s)")

    return is_valid, errors, warnings


def validate_file_permissions(file_path: str, required_perms: str = 'r') -> bool:
    """
    Validate file permissions.

    Args:
        file_path: Path to file to check
        required_perms: Required permissions ('r', 'w', 'x', or combinations)

    Returns:
        True if file has required permissions
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False

        if 'r' in required_perms and not os.access(path, os.R_OK):
            return False
        if 'w' in required_perms and not os.access(path, os.W_OK):
            return False
        if 'x' in required_perms and not os.access(path, os.X_OK):
            return False

        return True
    except Exception as e:
        logger.error(f"Error checking file permissions for {file_path}: {e}")
        return False


def validate_environment_variables() -> List[str]:
    """
    Get list of missing recommended environment variables.

    Returns:
        List of missing environment variable names
    """
    recommended_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'DATABASE_PATH',
        'SESSION_TIMEOUT',
        'COMMAND_TIMEOUT',
        'APP_BRAND'
    ]

    missing = []
    for var in recommended_vars:
        if var not in os.environ:
            missing.append(var)

    return missing
