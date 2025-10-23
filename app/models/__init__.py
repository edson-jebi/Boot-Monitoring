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

                # Create relay activation tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS relay_activations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        user_id INTEGER,
                        username TEXT,
                        is_automatic BOOLEAN DEFAULT 0,
                        success BOOLEAN DEFAULT 1,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')

                # Create indexes for relay activations
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_relay_activations_timestamp
                    ON relay_activations (timestamp DESC)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_relay_activations_device_id
                    ON relay_activations (device_id)
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


class RelayActivation:
    """Relay activation event tracking model."""

    def __init__(self, db: Database = None):
        self.db = db or Database()

    def log_activation(
        self,
        device_id: str,
        action: str,
        user_id: int = None,
        username: str = None,
        is_automatic: bool = False,
        success: bool = True
    ) -> bool:
        """
        Log a relay activation event.

        Args:
            device_id: Device identifier (e.g., 'RelayProcessor', 'LedScreen')
            action: Action performed ('on' or 'off')
            user_id: User ID who triggered the action (if manual)
            username: Username who triggered the action (if manual)
            is_automatic: True if triggered by schedule, False if manual
            success: Whether the activation was successful

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO relay_activations
                    (device_id, action, user_id, username, is_automatic, success, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (device_id, action, user_id, username, is_automatic, success))

                conn.commit()
                logger.debug(
                    f"Logged relay activation: device={device_id}, action={action}, "
                    f"user={username}, automatic={is_automatic}"
                )
                return True

        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to log relay activation: {e}")
            return False

    def get_activations(
        self,
        start_time: str = None,
        end_time: str = None,
        device_id: str = None,
        limit: int = 2000
    ) -> list:
        """
        Get relay activation events with optional filtering.

        Args:
            start_time: Start timestamp (ISO format or SQLite datetime)
            end_time: End timestamp (ISO format or SQLite datetime)
            device_id: Filter by specific device
            limit: Maximum number of records to return

        Returns:
            List of activation event dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                query = 'SELECT * FROM relay_activations WHERE 1=1'
                params = []

                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time)

                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time)

                if device_id:
                    query += ' AND device_id = ?'
                    params.append(device_id)

                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        except (DatabaseError, sqlite3.Error) as e:
            logger.error(f"Failed to get relay activations: {e}")
            return []


# Export classes for external use
__all__ = ['Database', 'User', 'Schedule', 'RelayActivation', 'DatabaseError', 'init_app_database']
