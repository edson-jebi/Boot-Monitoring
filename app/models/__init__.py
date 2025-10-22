"""
Database models for JEBI Web Application.
Handles user management and database operations.
"""
import sqlite3
import logging
import hashlib
from typing import Optional, Dict, Any
from contextlib import contextmanager
from config import get_config

# Try to import bcrypt, fall back to SHA-256 if not available
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt not available - using legacy SHA-256 hashing. Install bcrypt: pip install bcrypt==4.2.1")

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
                
                # Create schedule tables for device scheduling
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS device_schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schedule_days (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        schedule_id INTEGER NOT NULL,
                        day_of_week TEXT NOT NULL,
                        FOREIGN KEY (schedule_id) REFERENCES device_schedules (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_device_schedules_device_id 
                    ON device_schedules (device_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_device_schedules_enabled 
                    ON device_schedules (enabled)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_schedule_days_schedule_id 
                    ON schedule_days (schedule_id)
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
        """
        Hash password using bcrypt (preferred) or SHA-256 (fallback).

        Args:
            password: Plain text password to hash

        Returns:
            str: Bcrypt hashed password (if available) or SHA-256 hash
        """
        if BCRYPT_AVAILABLE:
            # Generate salt and hash password in one step
            # bcrypt automatically generates a random salt and includes it in the hash
            password_bytes = password.encode('utf-8')
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
            return hashed.decode('utf-8')
        else:
            # Fallback to SHA-256 with static salt (legacy mode)
            logger.warning("Using legacy SHA-256 password hashing. Install bcrypt for better security!")
            salt = "jebi_salt_2025"
            return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        Supports both bcrypt and legacy SHA-256 hashes for backward compatibility.

        Args:
            password: Plain text password to verify
            password_hash: Stored password hash (bcrypt or SHA-256)

        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
            if password_hash.startswith('$2'):
                if not BCRYPT_AVAILABLE:
                    logger.error("Password is bcrypt but bcrypt module not installed!")
                    return False
                password_bytes = password.encode('utf-8')
                hash_bytes = password_hash.encode('utf-8')
                return bcrypt.checkpw(password_bytes, hash_bytes)
            else:
                # Legacy SHA-256 hash verification
                logger.debug("Using legacy SHA-256 verification")
                salt = "jebi_salt_2025"
                computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return computed_hash == password_hash
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
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
        """
        Verify user credentials and return user data.

        Args:
            username: Username to verify
            password: Plain text password to verify

        Returns:
            Optional[Dict]: User data if authenticated, None otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # First, retrieve the user and their password hash
                cursor.execute(
                    '''SELECT id, username, password_hash, created_at, last_login
                       FROM users
                       WHERE username = ? AND is_active = 1''',
                    (username,)
                )
                user_row = cursor.fetchone()

                if user_row:
                    # Verify password using bcrypt
                    password_hash = user_row['password_hash']
                    if self.verify_password(password, password_hash):
                        # Update last login
                        cursor.execute(
                            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                            (user_row['id'],)
                        )
                        conn.commit()

                        logger.info(f"User '{username}' authenticated successfully")
                        # Return user data without password hash
                        user_data = dict(user_row)
                        del user_data['password_hash']
                        return user_data

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


class Schedule:
    """Schedule model for device scheduling."""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    def save_schedule(self, device_id: str, start_time: str, end_time: str, 
                     days: list, enabled: bool = False, user_id: int = None) -> bool:
        """Save or update a device schedule."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if schedule already exists for this device
                cursor.execute(
                    'SELECT id FROM device_schedules WHERE device_id = ?',
                    (device_id,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing schedule
                    schedule_id = existing['id']
                    cursor.execute('''
                        UPDATE device_schedules 
                        SET start_time = ?, end_time = ?, enabled = ?, 
                            updated_at = CURRENT_TIMESTAMP, user_id = ?
                        WHERE id = ?
                    ''', (start_time, end_time, enabled, user_id, schedule_id))
                    
                    # Delete existing days
                    cursor.execute('DELETE FROM schedule_days WHERE schedule_id = ?', (schedule_id,))
                else:
                    # Create new schedule
                    cursor.execute('''
                        INSERT INTO device_schedules (device_id, start_time, end_time, enabled, user_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (device_id, start_time, end_time, enabled, user_id))
                    schedule_id = cursor.lastrowid
                
                # Insert days
                for day in days:
                    cursor.execute('''
                        INSERT INTO schedule_days (schedule_id, day_of_week)
                        VALUES (?, ?)
                    ''', (schedule_id, day))
                
                conn.commit()
                logger.info(f"Schedule saved for device '{device_id}': {start_time}-{end_time}, days: {days}")
                return True
                
        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to save schedule for device '{device_id}': {e}")
            return False
    
    def get_schedule(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get schedule for a specific device."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get schedule details
                cursor.execute('''
                    SELECT id, device_id, start_time, end_time, enabled, 
                           created_at, updated_at, user_id
                    FROM device_schedules 
                    WHERE device_id = ?
                ''', (device_id,))
                schedule_row = cursor.fetchone()
                
                if not schedule_row:
                    return None
                
                schedule = dict(schedule_row)
                
                # Get days for this schedule
                cursor.execute('''
                    SELECT day_of_week 
                    FROM schedule_days 
                    WHERE schedule_id = ?
                ''', (schedule['id'],))
                days_rows = cursor.fetchall()
                schedule['days'] = [row['day_of_week'] for row in days_rows]
                
                return schedule
                
        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to get schedule for device '{device_id}': {e}")
            return None
    
    def get_all_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Get all device schedules."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all schedules
                cursor.execute('''
                    SELECT id, device_id, start_time, end_time, enabled, 
                           created_at, updated_at, user_id
                    FROM device_schedules
                ''')
                schedule_rows = cursor.fetchall()
                
                schedules = {}
                for schedule_row in schedule_rows:
                    schedule = dict(schedule_row)
                    device_id = schedule['device_id']
                    
                    # Get days for this schedule
                    cursor.execute('''
                        SELECT day_of_week 
                        FROM schedule_days 
                        WHERE schedule_id = ?
                    ''', (schedule['id'],))
                    days_rows = cursor.fetchall()
                    schedule['days'] = [row['day_of_week'] for row in days_rows]
                    
                    schedules[device_id] = schedule
                
                return schedules
                
        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to get all schedules: {e}")
            return {}
    
    def enable_schedule(self, device_id: str, enabled: bool = True) -> bool:
        """Enable or disable a schedule."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE device_schedules 
                    SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE device_id = ?
                ''', (enabled, device_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    status = "enabled" if enabled else "disabled"
                    logger.info(f"Schedule {status} for device '{device_id}'")
                    return True
                else:
                    logger.warning(f"No schedule found for device '{device_id}' to enable/disable")
                    return False
                    
        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to enable/disable schedule for device '{device_id}': {e}")
            return False
    
    def delete_schedule(self, device_id: str) -> bool:
        """Delete a schedule for a device."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM device_schedules WHERE device_id = ?', (device_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Schedule deleted for device '{device_id}'")
                    return True
                else:
                    logger.warning(f"No schedule found for device '{device_id}' to delete")
                    return False
                    
        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to delete schedule for device '{device_id}': {e}")
            return False


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


# Export classes for external use
__all__ = ['Database', 'User', 'Schedule', 'DatabaseError', 'init_app_database']
