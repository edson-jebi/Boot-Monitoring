"""
Base controller class for all route controllers.
"""
from abc import ABC, abstractmethod
from flask import Blueprint, session
from app.auth import login_required
from app.services import ServiceFactory
import logging

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """Base controller class for route handling."""
    
    def __init__(self, name: str, service_factory: ServiceFactory):
        self.service_factory = service_factory
        self.blueprint = Blueprint(name, __name__)
        self.logger = logger
        self._register_routes()
    
    @abstractmethod
    def _register_routes(self):
        """Register routes for this controller."""
        pass
    
    def get_current_user(self) -> str:
        """Get current logged-in username."""
        return session.get('username', 'anonymous')
    
    def log_user_action(self, action: str, details: str = None):
        """Log user action with context."""
        username = self.get_current_user()
        log_msg = f"User '{username}' performed action: {action}"
        if details:
            log_msg += f" - {details}"
        self.logger.info(log_msg)
