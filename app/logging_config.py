"""
Logging configuration for JEBI Web Application.
"""
import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(app_name: str = "jebi_web", log_level: str = "INFO") -> None:
    """Set up application logging."""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/{app_name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Security log handler
    security_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/security.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    security_handler.setFormatter(file_format)
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    
    logger.info(f"Logging initialized for {app_name}")


def get_security_logger():
    """Get security logger instance."""
    return logging.getLogger('security')
