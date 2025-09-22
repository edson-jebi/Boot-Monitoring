"""
Authentication module for JEBI Web Application.
Handles user authentication, session management, and security.
"""
import functools
import logging
from typing import Optional, Dict, Any
from flask import session, request, redirect, url_for, flash, current_app
from app.models import User

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self):
        self.user_model = User()
    
    def login_user(self, username: str, password: str) -> bool:
        """Authenticate and login user."""
        if not username or not password:
            flash('Username and password are required', 'error')
            return False
        
        # Validate input lengths
        if len(username) > 50 or len(password) > 100:
            flash('Invalid credentials', 'error')
            return False
        
        user = self.user_model.verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            logger.info(f"User '{username}' logged in successfully from {request.remote_addr}")
            return True
        else:
            flash('Invalid username or password', 'error')
            logger.warning(f"Failed login attempt for '{username}' from {request.remote_addr}")
            return False
    
    def logout_user(self) -> None:
        """Logout current user."""
        username = session.get('username', 'Unknown')
        session.clear()
        logger.info(f"User '{username}' logged out")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user."""
        user_id = session.get('user_id')
        if user_id:
            return self.user_model.get_user_by_id(user_id)
        return None
    
    def is_authenticated(self) -> bool:
        """Check if current user is authenticated."""
        return 'user_id' in session and 'username' in session


# Authentication decorators
def login_required(f):
    """Decorator to require authentication for routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            logger.warning(f"Unauthorized access attempt to {request.endpoint} from {request.remote_addr}")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Decorator to require user to be logged out."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = AuthManager()
        if auth_manager.is_authenticated():
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


# Rate limiting (simple implementation)
class RateLimiter:
    """Simple rate limiter for login attempts."""
    
    def __init__(self):
        self.attempts = {}
    
    def is_rate_limited(self, key: str, max_attempts: int = 5, window: int = 300) -> bool:
        """Check if key is rate limited."""
        import time
        current_time = time.time()
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Clean old attempts
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if current_time - attempt_time < window
        ]
        
        # Check if rate limited
        if len(self.attempts[key]) >= max_attempts:
            return True
        
        # Add current attempt
        self.attempts[key].append(current_time)
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()
