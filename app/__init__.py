"""
Application factory for JEBI Web Application.

This module implements the Flask application factory pattern, providing
a centralized way to create and configure the application instance with
proper security headers, database initialization, and blueprint registration.
"""
import logging
from datetime import timedelta
from typing import Optional
from flask import Flask
from config import get_config
from app.logging_config import setup_logging
from app.error_handlers import register_error_handlers
from app.models import init_app_database
from app.routes import auth_bp, main_bp

logger = logging.getLogger(__name__)


def create_app(environment: Optional[str] = None) -> Flask:
    """
    Application factory function with enhanced validation and error handling.

    Creates and configures a Flask application instance with:
    - Logging configuration
    - Database initialization
    - Security headers
    - Blueprint registration
    - Error handlers

    Args:
        environment: Environment name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV from environment or 'default'

    Returns:
        Flask: Configured Flask application instance

    Raises:
        ValueError: If configuration validation fails
        Exception: If database initialization fails
    """
    
    # Initialize logging first
    setup_logging("jebi_web", "INFO")
    logger = logging.getLogger(__name__)
    
    # Get the base directory (parent of app directory)
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(base_dir, 'templates')
    static_folder = os.path.join(base_dir, 'static')
    
    # Create Flask app with proper template and static folders
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # Load configuration
    config = get_config(environment)
    app.config.from_object(config)
    
    # Validate configuration
    try:
        from app.utils.config_validator import validate_application_config
        is_valid, errors, warnings = validate_application_config()
        
        if not is_valid:
            logger.error(f"Configuration validation failed: {errors}")
            raise ValueError(f"Invalid configuration: {errors}")
        
        if warnings:
            logger.warning(f"Configuration warnings: {warnings}")
            
    except ImportError:
        logger.warning("Configuration validator not available")
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
    
    # Set session timeout
    app.permanent_session_lifetime = timedelta(seconds=config.SESSION_TIMEOUT)
    
    # Initialize database
    with app.app_context():
        try:
            init_app_database()
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    # Register blueprints
    try:
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        logger.info("All blueprints registered successfully")
    except Exception as e:
        logger.error(f"Blueprint registration failed: {e}")
        raise
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add template globals
    @app.context_processor
    def inject_config():
        return {'config': config}
    
    # Add security headers and cache control
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if not config.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Add cache control headers for authenticated pages to prevent back button issues
        from flask import request, session
        if session.get('user_id') and request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    
    # Log application startup
    logger.info(f"JEBI Web Application created with environment: {environment or 'default'}")
    
    return app


# For backward compatibility and direct running
app = create_app()
