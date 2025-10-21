"""
Configuration module for JEBI Web Application.
Handles environment variables and application settings.
"""
import os
from typing import Optional


class Config:
    """Base configuration class."""
    
    # Security
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database
    DATABASE_PATH: str = os.environ.get('DATABASE_PATH') or 'users.db'
    
    # Server settings
    HOST: str = os.environ.get('HOST') or '0.0.0.0'
    PORT: int = int(os.environ.get('PORT') or 5000)
    DEBUG: bool = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Application settings
    APP_BRAND: str = os.environ.get('APP_BRAND') or "BRADKEN"  # Brand theme: BRADKEN or JEBI
    # APP_NAME automatically matches APP_BRAND unless explicitly overridden
    APP_NAME: str = os.environ.get('APP_NAME') or os.environ.get('APP_BRAND') or "BRADKEN"
    SESSION_TIMEOUT: int = int(os.environ.get('SESSION_TIMEOUT') or 3600)  # 1 hour
    
    # Command settings
    COMMAND_TIMEOUT: int = int(os.environ.get('COMMAND_TIMEOUT') or 10)
    DEFAULT_COMMAND: list = ['piTest', '-w', 'LedProcessor,1']
    
    # Default user credentials
    DEFAULT_USERNAME: str = os.environ.get('DEFAULT_USERNAME') or 'bradken'
    DEFAULT_PASSWORD: str = os.environ.get('DEFAULT_PASSWORD') or 'adminBradken25'
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if cls.SECRET_KEY == 'dev-key-change-in-production' and not cls.DEBUG:
            raise ValueError("SECRET_KEY must be set in production!")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            raise ValueError("PORT must be between 1 and 65535")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_PATH = 'dev_users.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    def __init__(self):
        super().__init__()
        # Override SECRET_KEY from environment
        if os.environ.get('SECRET_KEY'):
            self.SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def validate(cls) -> None:
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable must be set in production!")
        
        port = int(os.environ.get('PORT') or 5000)
        if port < 1 or port > 65535:
            raise ValueError("PORT must be between 1 and 65535")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_PATH = ':memory:'
    SECRET_KEY = 'testing-key'


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# Configuration revPi
config_map_revpi = {
    'RelayProcessor': "RelayProcessor",
    'RelayScreen': "RelayScreen",
    'LedProcessor': "LedProcessor",
    'LedScreen': "LedScreen",
    'RelayLight': "RelayLight",
    'LedLight': "LedLight",
}

# Parameter for revPi
device_map_path = "/home/pi/jebi-switchboard/config/strict_log_config.json"

# Path for log directory of jebi-switchboard service
log_path = "/var/log/jebi-switchboard"

def get_config(environment: Optional[str] = None) -> Config:
    """Get configuration based on environment."""
    env = environment or os.environ.get('FLASK_ENV', 'default')
    config_class = config_map.get(env, DevelopmentConfig)
    config_class.validate()
    return config_class
