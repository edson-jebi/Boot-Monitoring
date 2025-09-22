"""
Database models for JEBI Web Application.
Handles user management and database operations.
"""
import sqlite3
import hashlib
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class Database:
    """Database connection and operation manager."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def init_database(self) -> None:
        """Initialize database tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Create sessions table for better session management
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except DatabaseError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


class User:
    """User model for authentication and user management."""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt."""
        # In production, use bcrypt or Argon2 instead
        salt = "jebi_salt_2025"  # Should be random and stored securely
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user."""
        try:
            password_hash = self.hash_password(password)
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, password_hash)
                )
                conn.commit()
                logger.info(f"User '{username}' created successfully")
                return True
                
        except sqlite3.IntegrityError:
            logger.warning(f"User '{username}' already exists")
            return False
        except DatabaseError as e:
            logger.error(f"Failed to create user '{username}': {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user data."""
        try:
            password_hash = self.hash_password(password)
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT id, username, created_at, last_login 
                       FROM users 
                       WHERE username = ? AND password_hash = ? AND is_active = 1''',
                    (username, password_hash)
                )
                user_row = cursor.fetchone()
                
                if user_row:
                    # Update last login
                    cursor.execute(
                        'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                        (user_row['id'],)
                    )
                    conn.commit()
                    
                    logger.info(f"User '{username}' authenticated successfully")
                    return dict(user_row)
                
                logger.warning(f"Authentication failed for user '{username}'")
                return None
                
        except DatabaseError as e:
            logger.error(f"Authentication error for user '{username}': {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, username, created_at, last_login FROM users WHERE id = ? AND is_active = 1',
                    (user_id,)
                )
                user_row = cursor.fetchone()
                return dict(user_row) if user_row else None
                
        except DatabaseError as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    def create_default_user(self) -> None:
        """Create default user if it doesn't exist."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM users WHERE username = ?', 
                             (config.DEFAULT_USERNAME,))
                result = cursor.fetchone()
                
                if result['count'] == 0:
                    self.create_user(config.DEFAULT_USERNAME, config.DEFAULT_PASSWORD)
                    logger.info("Default user created")
                else:
                    logger.info("Default user already exists")
                    
        except DatabaseError as e:
            logger.error(f"Failed to create default user: {e}")


# Initialize database and create default user
def init_app_database():
    """Initialize application database."""
    try:
        user_model = User()
        user_model.create_default_user()
        logger.info("Application database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize application database: {e}")
        raise
